"""Keep a private record of every video and 3D task ModelArk accepted.

A task keeps running after a cancel that came too late or a restart, so its record is how it is collected.
"""

from __future__ import annotations

import re
import threading
from typing import TYPE_CHECKING
from ...types.tasks import TaskJob
from pydantic import ValidationError
from ...config.patterns import TASK_ID_PATTERN
from ...config.messages.tasks import JOB_UNKNOWN
from ...storage.files import save_file, read_file
from ...types.errors import ErrorCode, ByteplusError
from ...config.storage import JOB_FILES, MAX_FILE_BYTES
from ...config.generation.videos import JOB_LABEL_SEPARATOR, JOB_TIME_CHARACTERS

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Literal

# A task ID in ModelArk's documented form, which is also safe as a record's file name and in a URL path.
TASK_ID = re.compile(TASK_ID_PATTERN)


class JobStore:
    """Own the task records folder; every method blocks, so callers run it off the event loop."""

    def __init__(self, directory: Path) -> None:
        """Select the private jobs folder and the lock its files share across threads."""
        self.directory = directory
        self._lock = threading.Lock()

    def _read_all(self) -> list[TaskJob]:
        """Read every record; a damaged, oversized, or other-version file is skipped, so it never blocks the rest."""
        if not self.directory.is_dir():
            return []
        jobs: list[TaskJob] = []
        for path in sorted(self.directory.glob(f"*{JOB_FILES['SUFFIX']}")):
            try:
                jobs.append(TaskJob.model_validate_json(read_file(path, max_bytes=MAX_FILE_BYTES["JOB"])))
            except (OSError, ValidationError, ByteplusError):
                continue
        return jobs

    def save(self, job: TaskJob) -> None:
        """Write one record atomically, named by its task ID."""
        path = self.directory / f"{job.job_id}{JOB_FILES['SUFFIX']}"
        with self._lock:
            save_file(path, (job.model_dump_json(indent=2) + "\n").encode())

    def delete(self, job_id: str) -> None:
        """Delete one record; a record already gone needs no removal."""
        path = self.directory / f"{job_id}{JOB_FILES['SUFFIX']}"
        with self._lock:
            # reason: Record names are validated task IDs inside the private jobs folder.
            # bearer:disable python_lang_path_traversal
            path.unlink(missing_ok=True)

    def list_jobs(self, kind: Literal["videos", "meshes"]) -> list[TaskJob]:
        """List the recorded tasks of one kind, newest first."""
        with self._lock:
            jobs = [job for job in self._read_all() if job.kind == kind]
        return sorted(jobs, key=lambda job: job.submitted_at, reverse=True)

    def read(self, job_id: str) -> TaskJob:
        """Return the recorded task with this ID, whatever its kind; the caller checks the kind."""
        with self._lock:
            job = next((job for job in self._read_all() if job.job_id == job_id and TASK_ID.match(job_id)), None)
        if job is None:
            raise ByteplusError(ErrorCode.INVALID_INPUT, JOB_UNKNOWN)
        return job


def list_job_labels(jobs: JobStore, kind: Literal["videos", "meshes"]) -> list[str]:
    """List the recorded tasks of one kind as a Download node shows them: ID, model, and submit time in UTC.

    The submit time is cut to the minute, and ModelArk's own task ID leads, so the node can read it back.
    """
    labels: list[str] = []
    for job in jobs.list_jobs(kind):
        submitted = job.submitted_at[:JOB_TIME_CHARACTERS].replace("T", " ")
        labels.append(JOB_LABEL_SEPARATOR.join((job.job_id, job.model_id, submitted)))
    return labels


__all__ = ["TASK_ID", "JobStore", "list_job_labels"]
