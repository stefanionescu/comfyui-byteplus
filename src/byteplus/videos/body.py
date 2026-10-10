"""Check a Seedance request against its model's row and build the task body.

The mode decides the content items and their fixed order, and the row decides the fields the body may hold.
"""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from .modes import choose_video_mode
from typing import cast, TYPE_CHECKING
from ...types.images import EncodedImage
from ..options import build_request_body
from ...types.references import Reference
from ...types.errors import ErrorCode, ByteplusError
from ..models import validate_model, validate_range, validate_value
from ..references import validate_references, build_reference_parts
from ...config.generation.references import PART_TYPES, REFERENCE_ROLES
from ...config.generation.videos import DURATION, IMAGE_BOUNDS, RESOLUTIONS, ADAPTIVE_RATIO, ADAPTIVE_TASK_TYPES
from ...config.messages.inputs import (
    AUDIO_TOTAL,
    AUDIO_LENGTH,
    DRAFT_REUSED,
    RATIO_FIXED_ONLY,
    VIDEO_IMAGE_SIZE,
    AUDIO_NEEDS_MEDIA,
    DRAFT_FINISH_SIZE,
    VIDEO_MODE_LABELS,
    RATIO_ADAPTIVE_ONLY,
    VIDEO_REFERENCE_LIMIT,
    VIDEO_MODE_UNSUPPORTED,
    DRAFT_FINISH_UNSUPPORTED,
)

if TYPE_CHECKING:
    from ...types import Json
    from ...types.videos import VideoRequest
    from ...types.references import ReferenceKind
    from ...types.models import VideoRow, ModelMatch


def _validate_draft_finish(request: VideoRequest, match: ModelMatch[VideoRow]) -> None:
    """Refuse a draft the model cannot finish, at a size it does not finish at, or with settings the draft keeps."""
    limits = match.row.video
    if not limits.draft_finishes:
        raise ByteplusError(ErrorCode.INVALID_INPUT, DRAFT_FINISH_UNSUPPORTED.format(model=match.model_id))
    validate_references(request.references, frozenset({"draft"}), can_read_assets=False, now=datetime.now(UTC))
    if request.resolution not in limits.draft_finishes:
        message = DRAFT_FINISH_SIZE.format(model=match.model_id, resolutions=", ".join(limits.draft_finishes))
        raise ByteplusError(ErrorCode.INVALID_INPUT, message)
    is_changed = request.aspect_ratio is not None or request.has_sound is not None
    if is_changed or request.task_type != "auto" or request.is_camera_fixed:
        raise ByteplusError(ErrorCode.INVALID_INPUT, DRAFT_REUSED)
    if request.output_format is not None:
        validate_value(match, "file format", request.output_format, limits.output_formats)


def _validate_media(request: VideoRequest, match: ModelMatch[VideoRow], mode: str) -> None:
    """Refuse media the model does not read, a mode it does not take, references it cannot read, and too many.

    Only Seedance 2.5 and the 2.0 series take reference media, and they are the models that read assets. A frame
    that is a reference is checked for its expiry; an asset frame was refused when the socket was read.
    """
    limits = match.row.video
    chain = Counter(reference.kind for reference in request.references)
    counts: dict[ReferenceKind, int] = {
        "image": len(request.images) + chain["image"],
        "video": chain["video"],
        "audio": len(request.clips) + chain["audio"],
    }
    frames = [frame for frame in (request.first_frame, request.last_frame) if frame is not None]
    has_frames = bool(frames)
    validate_model(match, [kind for kind, count in counts.items() if count or (kind == "image" and has_frames)])
    if mode not in limits.modes:
        message = VIDEO_MODE_UNSUPPORTED.format(model=match.model_id, mode=VIDEO_MODE_LABELS[mode])
        raise ByteplusError(ErrorCode.INVALID_INPUT, message)
    maximums: dict[ReferenceKind, int] = {
        "image": limits.reference_images,
        "video": limits.reference_videos,
        "audio": limits.reference_audio,
    }
    kinds: frozenset[ReferenceKind] = frozenset(kind for kind, maximum in maximums.items() if maximum > 0)
    now = datetime.now(UTC)
    validate_references(request.references, kinds, can_read_assets=limits.reference_images > 0, now=now)
    linked = [frame for frame in frames if isinstance(frame, Reference)]
    validate_references(linked, frozenset({"image"}), can_read_assets=False, now=now)
    for kind, count in counts.items():
        if count > maximums[kind]:
            message = VIDEO_REFERENCE_LIMIT.format(model=match.model_id, maximum=maximums[kind], kind=kind, count=count)
            raise ByteplusError(ErrorCode.INVALID_INPUT, message)
    if counts["audio"] and counts["image"] + counts["video"] == 0 and not limits.can_use_audio_alone:
        raise ByteplusError(ErrorCode.INVALID_INPUT, AUDIO_NEEDS_MEDIA.format(model=match.model_id))


def _validate_images(request: VideoRequest) -> None:
    """Refuse a local image outside the sizes and shapes every Seedance model reads, frames first.

    Linked and output images are not measured; ModelArk checks them when it reads them.
    """
    labelled: list[tuple[str, EncodedImage | Reference | None]] = [
        ("first frame", request.first_frame),
        ("last frame", request.last_frame),
    ]
    labelled.extend(("reference images", image) for image in request.images)
    for label, image in labelled:
        if not isinstance(image, EncodedImage):
            continue
        short_side, long_side = sorted((image.width, image.height))
        is_sized = IMAGE_BOUNDS["MIN_SIDE"] <= short_side and long_side <= IMAGE_BOUNDS["MAX_SIDE"]
        if not is_sized or not IMAGE_BOUNDS["MIN_ASPECT"] <= image.width / image.height <= IMAGE_BOUNDS["MAX_ASPECT"]:
            message = VIDEO_IMAGE_SIZE.format(input=label, width=image.width, height=image.height)
            raise ByteplusError(ErrorCode.INVALID_INPUT, message)


def _validate_clips(request: VideoRequest, match: ModelMatch[VideoRow]) -> None:
    """Refuse a local clip outside the model's clip lengths, and clips longer in all than the model takes."""
    limits = match.row.video
    bounds, maximum_total = limits.reference_seconds, limits.reference_total_seconds
    # Only a model that takes reference audio has clip limits, and the media check refused clips for any other.
    if bounds is None or maximum_total is None:
        return
    minimum, maximum = bounds
    for clip in request.clips:
        if not minimum <= clip.seconds <= maximum:
            message = AUDIO_LENGTH.format(
                model=match.model_id, minimum=minimum, maximum=maximum, seconds=f"{clip.seconds:.1f}"
            )
            raise ByteplusError(ErrorCode.INVALID_INPUT, message)
    total = sum(clip.seconds for clip in request.clips)
    if total > maximum_total:
        message = AUDIO_TOTAL.format(model=match.model_id, maximum=maximum_total, seconds=f"{total:.1f}")
        raise ByteplusError(ErrorCode.INVALID_INPUT, message)


def _choose_length(request: VideoRequest, match: ModelMatch[VideoRow]) -> dict[str, Json]:
    """Choose the task type, resolution, and duration fields, each always sent where the model takes it.

    A draft is made at 480p whatever the resolution says. An edit always sends -1, since it matches the length of the
    video it edits, and so does 0, which lets the model choose.
    """
    limits = match.row.video
    fields: dict[str, Json] = {}
    if request.task_type != "auto":
        validate_value(match, "task", request.task_type, limits.task_types)
        fields["omni_reference_task_type"] = request.task_type
    if request.is_draft:
        validate_value(match, "draft", "on", ("on",) if limits.draft_finishes else ())
        fields["draft"] = True
        # RESOLUTIONS also holds the choices, so its values type as either; the draft size is text.
        fields["resolution"] = cast("str", RESOLUTIONS["DRAFT"])
    else:
        validate_value(match, "resolution", request.resolution, limits.resolutions)
        fields["resolution"] = request.resolution
    is_chosen = request.task_type == "edit" or request.duration == 0
    duration = DURATION["AUTO"] if is_chosen else request.duration
    extra = (DURATION["AUTO"],) if limits.can_choose_duration else ()
    validate_range(match, "duration", duration, limits.durations, extra)
    fields["duration"] = duration
    return fields


def _choose_ratio(request: VideoRequest, match: ModelMatch[VideoRow], mode: str) -> str | None:
    """Choose the ratio, judged for the mode, or for an edit or extend task, which keeps its video's shape.

    Where the model keeps the shape of its input, model default sends adaptive and a fixed ratio is refused; where it
    cannot choose a shape, adaptive is refused. Every Seedance model takes every other ratio.
    """
    limits = match.row.video
    is_adaptive_task = request.task_type in ADAPTIVE_TASK_TYPES
    label = VIDEO_MODE_LABELS[request.task_type if is_adaptive_task else mode]
    if mode in limits.adaptive_modes or is_adaptive_task:
        if request.aspect_ratio not in {None, ADAPTIVE_RATIO}:
            raise ByteplusError(ErrorCode.INVALID_INPUT, RATIO_ADAPTIVE_ONLY.format(model=match.model_id, mode=label))
        return ADAPTIVE_RATIO
    if mode in limits.fixed_ratio_modes and request.aspect_ratio == ADAPTIVE_RATIO:
        raise ByteplusError(ErrorCode.INVALID_INPUT, RATIO_FIXED_ONLY.format(model=match.model_id, mode=label))
    return request.aspect_ratio


def _choose_controls(request: VideoRequest, match: ModelMatch[VideoRow]) -> dict[str, Json]:
    """Choose sound, camera, file format, watermark, last frame, and seed.

    A draft returns no last frame; its output is the draft to finish. The seed is the one field left out silently,
    for a model that takes none.
    """
    limits = match.row.video
    fields: dict[str, Json] = {"watermark": request.has_watermark}
    if request.has_sound is not None:
        sound = "on" if request.has_sound else "off"
        validate_value(match, "generate audio", sound, ("on", "off") if limits.has_audio else ())
        fields["generate_audio"] = request.has_sound
    if request.is_camera_fixed:
        validate_value(match, "camera fixed", "on", ("on",) if limits.has_fixed_camera else ())
        fields["camera_fixed"] = True
    if request.output_format is not None:
        validate_value(match, "file format", request.output_format, limits.output_formats)
        fields["output_format"] = request.output_format
    if not request.is_draft:
        fields["return_last_frame"] = True
    if limits.has_seed:
        fields["seed"] = request.seed
    return fields


def _build_content(request: VideoRequest) -> list[Json]:
    """Build the content items: the text, the frames, then images, videos, and audio, local items before references.

    ModelArk names media by kind and position, Image 1 being the first image item, so this order is the numbering
    the prompt uses.
    """
    content: list[Json] = [{"type": "text", "text": request.prompt}] if request.prompt.strip() else []
    for role, frame in (("first_frame", request.first_frame), ("last_frame", request.last_frame)):
        if frame is not None:
            url = frame.url if isinstance(frame, EncodedImage) else frame.address
            content.append({"type": PART_TYPES["image"], PART_TYPES["image"]: {"url": url}, "role": role})
    local: dict[ReferenceKind, list[str]] = {
        "image": [image.url for image in request.images],
        "video": [],
        "audio": [clip.url for clip in request.clips],
    }
    for kind, urls in local.items():
        part = PART_TYPES[kind]
        content.extend({"type": part, part: {"url": url}, "role": REFERENCE_ROLES[kind]} for url in urls)
        content.extend(build_reference_parts([reference for reference in request.references if reference.kind == kind]))
    return content


def build_video_body(request: VideoRequest, match: ModelMatch[VideoRow]) -> dict[str, Json]:
    """Refuse, before anything is paid, what the model's row does not take, then build the body with Request Options.

    The first refusal stops the check. Finishing a draft sends only the draft and the settings ModelArk lets a finish
    change; ModelArk reuses the rest from the draft and refuses it if sent again.
    """
    mode = choose_video_mode(request)
    if mode == "draft":
        _validate_draft_finish(request, match)
        body: dict[str, Json] = {
            "model": match.model_id,
            "content": list(build_reference_parts(request.references)),
            "resolution": request.resolution,
            "watermark": request.has_watermark,
            "return_last_frame": True,
        }
        if request.output_format is not None:
            body["output_format"] = request.output_format
    else:
        _validate_media(request, match, mode)
        _validate_images(request)
        _validate_clips(request, match)
        body = {"model": match.model_id, "content": _build_content(request), **_choose_length(request, match)}
        ratio = _choose_ratio(request, match, mode)
        if ratio is not None:
            body["ratio"] = ratio
        body |= _choose_controls(request, match)
    return build_request_body(body, request.options, "videos", match.row)


__all__ = ["build_video_body"]
