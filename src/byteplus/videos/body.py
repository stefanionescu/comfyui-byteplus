"""Check a Seedance request against its model's row and build the task body.

The mode decides the content items and their fixed order, and the row decides the fields the body may hold.
"""

from __future__ import annotations

from ...config.media import WAV
from datetime import UTC, datetime
from .modes import choose_video_mode
from typing import cast, TYPE_CHECKING
from ...types.images import EncodedImage
from ..options import build_request_body
from ...types.references import Reference
from ..models import validate_range, validate_value
from ...types.errors import ErrorCode, ByteplusError
from ..references import validate_references, build_reference_parts
from ...config.generation.references import PART_TYPES, REFERENCE_ROLES
from ...config.generation.videos import DURATION, RESOLUTIONS, ADAPTIVE_RATIO, ADAPTIVE_TASK_TYPES
from ...config.messages.inputs import (
    RATIO_FIXED_ONLY,
    DRAFT_FINISH_SIZE,
    VIDEO_MODE_LABELS,
    RATIO_ADAPTIVE_ONLY,
    VIDEO_MODE_UNSUPPORTED,
    DRAFT_FINISH_UNSUPPORTED,
)

if TYPE_CHECKING:
    from ...types import Json
    from ...types.videos import VideoRequest
    from ...types.references import ReferenceKind
    from ...types.models import VideoRow, ModelMatch


def _validate_draft_finish(request: VideoRequest, match: ModelMatch[VideoRow]) -> None:
    """Refuse a draft the model cannot finish, or at a size it does not finish at."""
    limits = match.row.video
    if not limits.draft_finishes:
        raise ByteplusError(ErrorCode.INVALID_INPUT, DRAFT_FINISH_UNSUPPORTED.format(model=match.model_id))
    validate_references(request.references, ("draft",), can_read_assets=False, now=datetime.now(UTC))
    if request.resolution not in limits.draft_finishes:
        message = DRAFT_FINISH_SIZE.format(model=match.model_id, resolutions=", ".join(limits.draft_finishes))
        raise ByteplusError(ErrorCode.INVALID_INPUT, message)
    if request.output_format is not None:
        validate_value(match, "output format", request.output_format, limits.output_formats)


def _validate_media(request: VideoRequest, match: ModelMatch[VideoRow], mode: str) -> None:
    """Refuse a mode the model does not take, and references it cannot read or that expire too soon.

    Only Seedance 2.5 and the 2.0 series take reference media, so past the mode check references reach only models
    that read every kind of them, assets included. A frame may be an output or a link, not an asset.
    """
    if mode not in match.row.video.modes:
        message = VIDEO_MODE_UNSUPPORTED.format(model=match.model_id, mode=VIDEO_MODE_LABELS[mode])
        raise ByteplusError(ErrorCode.INVALID_INPUT, message)
    now = datetime.now(UTC)
    validate_references(request.references, ("image", "video", "audio"), can_read_assets=True, now=now)
    frames = [frame for frame in (request.first_frame, request.last_frame) if isinstance(frame, Reference)]
    validate_references(frames, ("image",), can_read_assets=False, now=now)


def _choose_length(request: VideoRequest, match: ModelMatch[VideoRow]) -> dict[str, Json]:
    """Choose the task type, resolution, and duration fields, each always sent where the model takes it.

    A draft is made at 480p whatever the resolution says. An edit always sends -1, since it matches the length of the
    video it edits.
    """
    limits = match.row.video
    fields: dict[str, Json] = {}
    if request.task_type != "auto":
        validate_value(match, "omni reference task type", request.task_type, limits.task_types)
        fields["omni_reference_task_type"] = request.task_type
    if request.is_draft:
        validate_value(match, "draft", "true", ("true",) if limits.draft_finishes else ())
        fields["draft"] = True
        # RESOLUTIONS also holds the choices, so its values type as either; the draft size is text.
        fields["resolution"] = cast("str", RESOLUTIONS["DRAFT"])
    else:
        validate_value(match, "resolution", request.resolution, limits.resolutions)
        fields["resolution"] = request.resolution
    duration = DURATION["AUTO"] if request.task_type == "edit" else request.duration
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
        if request.ratio not in {None, ADAPTIVE_RATIO}:
            raise ByteplusError(ErrorCode.INVALID_INPUT, RATIO_ADAPTIVE_ONLY.format(model=match.model_id, mode=label))
        return ADAPTIVE_RATIO
    if mode in limits.fixed_ratio_modes and request.ratio == ADAPTIVE_RATIO:
        raise ByteplusError(ErrorCode.INVALID_INPUT, RATIO_FIXED_ONLY.format(model=match.model_id, mode=label))
    return request.ratio


def _choose_controls(request: VideoRequest, match: ModelMatch[VideoRow]) -> dict[str, Json]:
    """Choose sound, camera, output format, watermark, last frame, and seed.

    A draft returns no last frame; its output is the draft to finish. The seed is the one field left out silently,
    for a model that takes none.
    """
    limits = match.row.video
    fields: dict[str, Json] = {"watermark": request.has_watermark}
    if request.has_sound is not None:
        sound = "true" if request.has_sound else "false"
        validate_value(match, "generate audio", sound, ("true", "false") if limits.has_audio else ())
        fields["generate_audio"] = request.has_sound
    if request.is_camera_fixed:
        validate_value(match, "camera fixed", "true", ("true",) if limits.has_fixed_camera else ())
        fields["camera_fixed"] = True
    if request.output_format is not None:
        validate_value(match, "output format", request.output_format, limits.output_formats)
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
        "audio": [WAV["URL_PREFIX"] + clip for clip in request.clips],
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
        body = {"model": match.model_id, "content": _build_content(request), **_choose_length(request, match)}
        ratio = _choose_ratio(request, match, mode)
        if ratio is not None:
            body["ratio"] = ratio
        body |= _choose_controls(request, match)
    return build_request_body(body, request.options, "videos", match.row)


__all__ = ["build_video_body"]
