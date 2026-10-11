"""Check a Seedance request against its model's row, build the task body, and build the task that sends it.

The mode decides the content items and their fixed order, and the row decides the fields the body can hold.
"""

from __future__ import annotations

from functools import partial
from ...config.media import WAV
from typing import TYPE_CHECKING
from ...types.tasks import TaskRequest
from ...types.images import EncodedImage
from ..options import build_request_body
from ...types.references import Reference
from ..tasks.operation import TaskOperation
from ..references import validate_references
from ..models import find_model, validate_value
from ...types.errors import ErrorCode, BytePlusError
from .modes import choose_video_mode, validate_video_request
from ...config.messages.models import MODEL_FIELD, MODEL_RANGE, MODEL_RANGE_EXTRA
from ...config.generation.videos import DURATION, ADAPTIVE_RATIO, DRAFT_RESOLUTION, ADAPTIVE_TASK_TYPES
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
    from ..tasks.records import TaskStore
    from ...types.videos import VideoRequest
    from ...types.models import VideoRow, ModelMatch


def _validate_draft_finish(request: VideoRequest, match: ModelMatch[VideoRow]) -> None:
    """Refuse a draft finish the model does not take, or a resolution it cannot finish a draft at."""
    limits = match.row.video
    if not limits.draft_resolutions:
        raise BytePlusError(ErrorCode.INVALID_INPUT, DRAFT_FINISH_UNSUPPORTED.format(model=match.model_id))
    validate_references(request.references, ("draft",), can_read_assets=False)
    if request.resolution not in limits.draft_resolutions:
        message = DRAFT_FINISH_SIZE.format(model=match.model_id, resolutions=", ".join(limits.draft_resolutions))
        raise BytePlusError(ErrorCode.INVALID_INPUT, message)
    if request.output_format is not None:
        validate_value(match, "output_format", request.output_format, limits.output_formats)


def _validate_media(request: VideoRequest, match: ModelMatch[VideoRow], mode: str) -> None:
    """Refuse a mode the model does not take, and references it cannot read or that expire too soon.

    Only Seedance 2.5 and the 2.0 series take reference media, and they read every kind of reference, assets
    included. A frame can be an output or a link, not an asset.
    """
    if mode not in match.row.video.modes:
        message = VIDEO_MODE_UNSUPPORTED.format(model=match.model_id, mode=VIDEO_MODE_LABELS[mode])
        raise BytePlusError(ErrorCode.INVALID_INPUT, message)
    validate_references(request.references, ("image", "video", "audio"), can_read_assets=True)
    frames = [frame for frame in (request.first_frame, request.last_frame) if isinstance(frame, Reference)]
    validate_references(frames, ("image",), can_read_assets=False)


def _choose_duration(request: VideoRequest, match: ModelMatch[VideoRow]) -> int:
    """Choose the duration, refusing one outside the model's range; -1 lets a model that can choose pick the length.

    An edit always sends -1, since it matches the length of the video it edits.
    """
    limits = match.row.video
    duration = DURATION["AUTO"] if request.omni_reference_task_type == "edit" else request.duration
    minimum, maximum = limits.durations
    if minimum <= duration <= maximum or (limits.can_choose_duration and duration == DURATION["AUTO"]):
        return duration
    fields = {"model": match.model_id, "field": "duration", "minimum": minimum, "maximum": maximum}
    if limits.can_choose_duration:
        raise BytePlusError(ErrorCode.INVALID_INPUT, MODEL_RANGE_EXTRA.format(**fields, extra=DURATION["AUTO"]))
    raise BytePlusError(ErrorCode.INVALID_INPUT, MODEL_RANGE.format(**fields))


def _choose_task_fields(request: VideoRequest, match: ModelMatch[VideoRow]) -> dict[str, Json]:
    """Choose the task type, resolution, and duration fields.

    The task type is sent only when it is not auto. A draft is made at 480p whatever the resolution says.
    """
    limits = match.row.video
    fields: dict[str, Json] = {}
    if request.omni_reference_task_type != "auto":
        validate_value(
            match, "omni_reference_task_type", request.omni_reference_task_type, limits.omni_reference_task_types
        )
        fields["omni_reference_task_type"] = request.omni_reference_task_type
    if request.is_draft:
        if not limits.draft_resolutions:
            raise BytePlusError(ErrorCode.INVALID_INPUT, MODEL_FIELD.format(model=match.model_id, field="draft"))
        fields["draft"] = True
        fields["resolution"] = DRAFT_RESOLUTION
    else:
        validate_value(match, "resolution", request.resolution, limits.resolutions)
        fields["resolution"] = request.resolution
    fields["duration"] = _choose_duration(request, match)
    return fields


def _choose_ratio(request: VideoRequest, match: ModelMatch[VideoRow], mode: str) -> str | None:
    """Choose the ratio for the mode, or for an edit or extend task, which keeps its video's shape.

    Where the model keeps the shape of its input, model default sends adaptive and a fixed ratio is refused. Where it
    cannot choose a shape, adaptive is refused. Every Seedance model takes every other ratio.
    """
    limits = match.row.video
    is_adaptive_task = request.omni_reference_task_type in ADAPTIVE_TASK_TYPES
    label = VIDEO_MODE_LABELS[request.omni_reference_task_type if is_adaptive_task else mode]
    if mode in limits.adaptive_modes or is_adaptive_task:
        if request.ratio not in {None, ADAPTIVE_RATIO}:
            raise BytePlusError(ErrorCode.INVALID_INPUT, RATIO_ADAPTIVE_ONLY.format(model=match.model_id, mode=label))
        return ADAPTIVE_RATIO
    if mode in limits.fixed_ratio_modes and request.ratio == ADAPTIVE_RATIO:
        raise BytePlusError(ErrorCode.INVALID_INPUT, RATIO_FIXED_ONLY.format(model=match.model_id, mode=label))
    return request.ratio


def _choose_controls(request: VideoRequest, match: ModelMatch[VideoRow]) -> dict[str, Json]:
    """Choose sound, camera, output format, watermark, last frame, and seed.

    A draft returns no last frame; its output is the draft to finish. The seed is the one field left out silently,
    for a model that takes none.
    """
    limits = match.row.video
    fields: dict[str, Json] = {"watermark": request.has_watermark}
    if request.has_audio is not None:
        if not limits.has_audio:
            raise BytePlusError(
                ErrorCode.INVALID_INPUT, MODEL_FIELD.format(model=match.model_id, field="generate_audio")
            )
        fields["generate_audio"] = request.has_audio
    if request.is_camera_fixed:
        if not limits.has_fixed_camera:
            raise BytePlusError(ErrorCode.INVALID_INPUT, MODEL_FIELD.format(model=match.model_id, field="camera_fixed"))
        fields["camera_fixed"] = True
    if request.output_format is not None:
        validate_value(match, "output_format", request.output_format, limits.output_formats)
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
            content.append({"type": "image_url", "image_url": {"url": url}, "role": role})
    local = {
        "image": [image.url for image in request.images],
        "audio": [WAV["URL_PREFIX"] + clip for clip in request.clips],
    }
    for kind in ("image", "video", "audio"):
        urls = [
            *local.get(kind, ()),
            *(reference.address for reference in request.references if reference.kind == kind),
        ]
        content.extend(
            {"type": f"{kind}_url", f"{kind}_url": {"url": url}, "role": f"reference_{kind}"} for url in urls
        )
    return content


def _build_video_body(request: VideoRequest) -> dict[str, Json]:
    """Refuse, before anything is paid, what the model's row does not take, then build the body with Request Options.

    Finishing a draft sends only the draft and the settings a finish can change. ModelArk reuses the rest from the
    draft, and refuses the request if the rest is sent again.
    """
    match = find_model(request.model_id, "videos")
    mode = choose_video_mode(request)
    if mode == "draft":
        _validate_draft_finish(request, match)
        body: dict[str, Json] = {
            "model": match.model_id,
            "content": [{"type": "draft_task", "draft_task": {"id": draft.address}} for draft in request.references],
            "resolution": request.resolution,
            "watermark": request.has_watermark,
            "return_last_frame": True,
        }
        if request.output_format is not None:
            body["output_format"] = request.output_format
    else:
        _validate_media(request, match, mode)
        body = {"model": match.model_id, "content": _build_content(request), **_choose_task_fields(request, match)}
        ratio = _choose_ratio(request, match, mode)
        if ratio is not None:
            body["ratio"] = ratio
        body |= _choose_controls(request, match)
    return build_request_body(body, request.options, "videos", match.row)


def build_video_operation(request: VideoRequest, tasks: TaskStore) -> TaskOperation:
    """Build the task that checks the Seedance request, sends it, and records it, as a draft when it makes one."""
    validate_request = partial(validate_video_request, request)
    build_body = partial(_build_video_body, request)
    return TaskOperation(TaskRequest("videos", request.model_id, validate_request, build_body, request.is_draft), tasks)


__all__ = ["build_video_operation"]
