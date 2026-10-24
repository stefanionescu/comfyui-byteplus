"""Video and 3D tasks: what a node asks for, the record kept while a task runs, the create request, and the result."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal
from dataclasses import dataclass

from . import Value
from .options import ModelRequest

if TYPE_CHECKING:
    from collections.abc import Mapping, Callable

    from . import Json
    from .images import EncodedImage
    from .settings import Settings
    from .references import Reference, OutputFile


@dataclass(frozen=True, slots=True, kw_only=True)
class VideoRequest(ModelRequest):
    """One Seedance request with its local media already encoded; None means default.

    Attributes:
        prompt: What the video shows; empty to finish a draft.
        duration: The length in seconds; -1 lets the model choose.
        resolution: The resolution to send; Seedance makes a draft at 480p instead.
        ratio: The aspect ratio, or adaptive.
        has_audio: The generate_audio value: whether the video has sound.
        omni_reference_task_type: auto, reference, edit, or extend; auto sends nothing.

        is_draft: Whether to make a 480p draft.
        is_camera_fixed: Whether to ask the model to keep the camera still.
        output_format: mp4 or mov.
        has_watermark: Whether ModelArk marks the video as AI-generated.

        first_frame: The image the video starts from: encoded here, or a reference ModelArk reads by address.
        last_frame: The image the video ends on, in the same forms.
        images: The images connected to reference_image, in list order, then batch order.
        clips: The clips connected to reference_audio as base64 WAV, in list order, then batch order.
        references: The references chain, in chain order.
        seed: The seed, sent only to models that take one.

    """

    prompt: str
    duration: int
    resolution: str
    ratio: str | None
    has_audio: bool | None
    omni_reference_task_type: str
    is_draft: bool
    is_camera_fixed: bool
    output_format: str | None
    has_watermark: bool
    first_frame: EncodedImage | Reference | None
    last_frame: EncodedImage | Reference | None
    images: tuple[EncodedImage, ...]
    clips: tuple[str, ...]
    references: tuple[Reference, ...]
    seed: int


@dataclass(frozen=True, slots=True, kw_only=True)
class MeshRequest(ModelRequest):
    """One 3D request with its images already encoded.

    Attributes:
        prompt: What to make and the model's own --name value commands, trimmed; empty when the model works from
            images alone.
        images: The images connected to images, in list order, then batch order.
        references: The image references, in chain order, which ModelArk reads after the images.

    """

    prompt: str
    images: tuple[EncodedImage, ...]
    references: tuple[Reference, ...]


class TaskRecord(Value):
    """One task ModelArk accepted, recorded before the first wait so a download node can collect it if it keeps running.

    Attributes:
        version: File format version; the extension refuses any other.
        task_id: ModelArk's task ID, which also names the record's file.
        kind: The kind of node that made it, videos or meshes, which lists and collects it.
        model_id: The model ID as typed.
        submitted_at: When the extension sent the create request, as an ISO 8601 time in UTC.
        is_draft: Whether it is a Seedance draft, whose output is a draft reference.

    """

    version: Literal[1]
    task_id: str
    kind: Literal['videos', 'meshes']
    model_id: str
    submitted_at: str
    is_draft: bool


@dataclass(frozen=True, slots=True)
class TaskRequest:
    """One video or 3D task to create, which carries the checks and the body of its kind.

    Attributes:
        kind: videos or meshes: the record's kind.
        model_id: The model ID as typed.
        validate_request: The checks that need no model row, the upload limit included.
        build_body: Finds the model's row, runs its checks, and builds the body with Request Options merged.
        is_draft: Whether the task makes a Seedance draft.

    """

    kind: Literal['videos', 'meshes']
    model_id: str
    validate_request: Callable[[Settings], None]
    build_body: Callable[[], Mapping[str, Json]]
    is_draft: bool


@dataclass(frozen=True, slots=True)
class TaskResult:
    """What one finished task made.

    Attributes:
        record: The task's record.
        outputs: Each downloaded file, keyed by its reply field: video_url, last_frame_url, or file_url.
        created_at: When ModelArk accepted the task, in Unix seconds.

    """

    record: TaskRecord
    outputs: Mapping[str, OutputFile]
    created_at: int


__all__ = ['MeshRequest', 'TaskRecord', 'TaskRequest', 'TaskResult', 'VideoRequest']
