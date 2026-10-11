"""Tell what a Seedance request starts from, and refuse what no model could take before the model row is read."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from ...types.images import EncodedImage
from ..operation import validate_upload_size
from ...config.patterns import VIDEO_COMMAND_PATTERN
from ...types.errors import ErrorCode, BytePlusError
from ...config.generation.videos import ADAPTIVE_TASK_TYPES
from ...config.messages.inputs import (
    DRAFT_ALONE,
    DRAFT_TWICE,
    VIDEO_EMPTY,
    DRAFT_SINGLE,
    PROMPT_COMMAND,
    LAST_FRAME_ALONE,
    TASK_NEEDS_VIDEO,
    TASK_NEEDS_REFERENCES,
    FRAMES_BESIDE_REFERENCES,
)

if TYPE_CHECKING:
    from ...types.settings import Settings
    from ...types.videos import VideoRequest

# Prompt text Seedance would read as a setting, such as "--rs 720p".
_VIDEO_COMMAND = re.compile(VIDEO_COMMAND_PATTERN)


def _validate_draft(request: VideoRequest) -> None:
    """Refuse a draft to finish beside anything else, more than one, or with draft on; ModelArk reuses the rest."""
    drafts = [reference for reference in request.references if reference.kind == "draft"]
    if len(drafts) > 1:
        raise BytePlusError(ErrorCode.INVALID_INPUT, DRAFT_SINGLE.format(count=len(drafts)))
    has_frames = request.first_frame is not None or request.last_frame is not None
    if request.prompt.strip() or has_frames or request.images or request.clips or len(request.references) > 1:
        raise BytePlusError(ErrorCode.INVALID_INPUT, DRAFT_ALONE)
    if request.is_draft:
        raise BytePlusError(ErrorCode.INVALID_INPUT, DRAFT_TWICE)


def _validate_sources(request: VideoRequest, mode: str) -> None:
    """Refuse a request with nothing to make a video from, frames beside reference media, and a task without them."""
    if mode == "text" and not request.prompt.strip() and request.last_frame is None:
        raise BytePlusError(ErrorCode.INVALID_INPUT, VIDEO_EMPTY)
    if request.last_frame is not None and request.first_frame is None:
        raise BytePlusError(ErrorCode.INVALID_INPUT, LAST_FRAME_ALONE)
    if request.first_frame is not None and (request.images or request.clips or request.references):
        raise BytePlusError(ErrorCode.INVALID_INPUT, FRAMES_BESIDE_REFERENCES)
    if request.omni_reference_task_type != "auto" and mode != "references":
        raise BytePlusError(
            ErrorCode.INVALID_INPUT, TASK_NEEDS_REFERENCES.format(task=request.omni_reference_task_type)
        )
    has_video = any(reference.kind == "video" for reference in request.references)
    if request.omni_reference_task_type in ADAPTIVE_TASK_TYPES and not has_video:
        raise BytePlusError(ErrorCode.INVALID_INPUT, TASK_NEEDS_VIDEO.format(task=request.omni_reference_task_type))


def choose_video_mode(request: VideoRequest) -> str:
    """Choose what the video starts from: a draft to finish, frames, reference media, or a prompt alone."""
    if any(reference.kind == "draft" for reference in request.references):
        return "draft"
    if request.first_frame is not None:
        return "first_last_frame" if request.last_frame is not None else "first_frame"
    if request.images or request.clips or request.references:
        return "references"
    return "text"


def validate_video_request(request: VideoRequest, settings: Settings) -> None:
    """Refuse, before anything is sent, a request no model could take, and local media over the upload limit."""
    command = _VIDEO_COMMAND.search(request.prompt)
    if command is not None:
        raise BytePlusError(ErrorCode.INVALID_INPUT, PROMPT_COMMAND.format(command=command.group().strip()))
    mode = choose_video_mode(request)
    if mode == "draft":
        _validate_draft(request)
    else:
        _validate_sources(request, mode)
    frames = [frame.url for frame in (request.first_frame, request.last_frame) if isinstance(frame, EncodedImage)]
    images = [image.url for image in request.images]
    validate_upload_size((*frames, *images, *request.clips), settings)


__all__ = ["choose_video_mode", "validate_video_request"]
