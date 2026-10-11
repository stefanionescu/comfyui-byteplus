"""Video and 3D task records: the file kept while a task runs, the request that creates one, and what it made."""

from __future__ import annotations

from . import Value
from dataclasses import dataclass
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from . import Json
    from .settings import Settings
    from .references import OutputFile
    from collections.abc import Mapping, Callable


class TaskRecord(Value):
    """One task ModelArk accepted, recorded before the first wait so a task that keeps running can be collected.

    Attributes:
        version: File format version; any other is refused.
        task_id: ModelArk's task ID, which also names the record's file.
        kind: The kind of node that made it, videos or meshes, which lists and collects it.
        model_id: The model ID as typed.
        submitted_at: When the create request was sent, in ISO 8601 and UTC.
        is_draft: Whether it is a Seedance draft, whose output is a draft reference.

    """

    version: Literal[1]
    task_id: str
    kind: Literal["videos", "meshes"]
    model_id: str
    submitted_at: str
    is_draft: bool = False


@dataclass(frozen=True, slots=True)
class TaskRequest:
    """One video or 3D task to create, with the checks and the body of its kind.

    Attributes:
        kind: videos or meshes: the record's kind.
        model_id: The model ID as typed.
        validate_request: The checks that need no model row, the upload limit included.
        build_body: Finds the model's row, runs its checks, and builds the body with Request Options merged.
        is_draft: Whether the task makes a Seedance draft.

    """

    kind: Literal["videos", "meshes"]
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
        updated_at: When the task last changed status, in Unix seconds.

    """

    record: TaskRecord
    outputs: Mapping[str, OutputFile]
    created_at: int
    updated_at: int


__all__ = ["TaskRecord", "TaskRequest", "TaskResult"]
