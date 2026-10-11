"""Keep a private record of every video and 3D task ModelArk accepted.

A task keeps running after a cancel that came too late or a restart, so its record is how it is collected.
"""

from __future__ import annotations

import re
import threading
from typing import TYPE_CHECKING
from pydantic import ValidationError
from ...types.tasks import TaskRecord
from ...config.patterns import TASK_ID_PATTERN
from ...config.messages.tasks import TASK_UNKNOWN
from ...storage.files import save_file, read_file
from ...types.errors import ErrorCode, BytePlusError
from ...config.storage import TASK_FILES, MAX_FILE_BYTES
from ...config.generation.videos import TASK_LABEL_SEPARATOR, TASK_TIME_CHARACTERS

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Literal

# A task ID in ModelArk's documented form, which is also safe as a record's file name and in a URL path.
TASK_ID = re.compile(TASK_ID_PATTERN)


class TaskStore:
    """Own the task records folder; every method blocks, so callers run it off the event loop."""

    def __init__(self, directory: Path) -> None:
        """Select the private tasks folder and the lock its files share across threads."""
        self.directory = directory
        self._lock = threading.Lock()

    def _read_all(self) -> list[TaskRecord]:
        """Read every record; a damaged, oversized, or other-version file is skipped, so it never blocks the rest."""
        if not self.directory.is_dir():
            return []
        tasks: list[TaskRecord] = []
        for path in sorted(self.directory.glob(f"*{TASK_FILES['SUFFIX']}")):
            try:
                tasks.append(TaskRecord.model_validate_json(read_file(path, max_bytes=MAX_FILE_BYTES["TASK"])))
            except (OSError, ValidationError, BytePlusError):
                continue
        return tasks

    def save(self, record: TaskRecord) -> None:
        """Write one record atomically, named by its task ID."""
        path = self.directory / f"{record.task_id}{TASK_FILES['SUFFIX']}"
        with self._lock:
            save_file(path, (record.model_dump_json(indent=2) + "\n").encode())

    def delete(self, task_id: str) -> None:
        """Delete one record; a record already gone needs no removal."""
        path = self.directory / f"{task_id}{TASK_FILES['SUFFIX']}"
        with self._lock:
            # reason: Record names are validated task IDs inside the private tasks folder.
            # bearer:disable python_lang_path_traversal
            path.unlink(missing_ok=True)

    def list_records(self, kind: Literal["videos", "meshes"]) -> list[TaskRecord]:
        """List the recorded tasks of one kind, newest first."""
        with self._lock:
            tasks = [record for record in self._read_all() if record.kind == kind]
        return sorted(tasks, key=lambda record: record.submitted_at, reverse=True)

    def read(self, task_id: str) -> TaskRecord:
        """Return the recorded task with this ID, whatever its kind; the caller checks the kind."""
        with self._lock:
            record = next(
                (record for record in self._read_all() if record.task_id == task_id and TASK_ID.match(task_id)), None
            )
        if record is None:
            raise BytePlusError(ErrorCode.INVALID_INPUT, TASK_UNKNOWN)
        return record


def list_task_labels(tasks: TaskStore, kind: Literal["videos", "meshes"]) -> list[str]:
    """List the recorded tasks of one kind as a Download node shows them: ID, model, and submit time in UTC.

    The submit time is cut to the minute, and ModelArk's own task ID leads, so the node can read it back.
    """
    labels: list[str] = []
    for record in tasks.list_records(kind):
        submitted = record.submitted_at[:TASK_TIME_CHARACTERS].replace("T", " ")
        labels.append(TASK_LABEL_SEPARATOR.join((record.task_id, record.model_id, submitted)))
    return labels


__all__ = ["TASK_ID", "TaskStore", "list_task_labels"]
