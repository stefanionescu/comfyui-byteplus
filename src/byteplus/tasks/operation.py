"""Create a video or 3D task and record it as soon as ModelArk accepts it, then wait for it and download what it made.

A cancel while the task is queued cancels it, which bills nothing; a task that started runs on and stays recorded.
"""

from __future__ import annotations

import time
import asyncio
from .jobs import TASK_ID
from ..models import find_model
from ..failures import build_failure
from pydantic import ValidationError
from typing import cast, TYPE_CHECKING
from datetime import UTC, datetime, timedelta
from ...config.messages.run import REPLY_UNREADABLE
from ...types.errors import ErrorCode, ByteplusError
from ...config.byteplus import TASK_URL, ENDPOINT_URLS
from ...types.replies import TaskReply, TaskCreateReply
from ...types.tasks import TaskJob, TaskOutput, TaskResult
from ...config.generation.references import OUTPUT_LIFETIME_SECONDS
from ..transport import send_json, send_lookup, download_output, send_task_cancel
from ...config.messages.tasks import TASK_GONE, TASK_OUTCOMES, TASK_UNRECORDED, TASK_FILES_EXPIRED
from ...config.generation.videos import CONTENT_FIELDS, DONE_STATUSES, CANCELLABLE_STATUS, TASK_RETENTION_SECONDS

if TYPE_CHECKING:
    from ...types import Json
    from .jobs import JobStore
    from collections.abc import Mapping
    from ...types.tasks import TaskRequest
    from ...types.models import ModelRow, ModelMatch
    from ...types.settings import Settings, Configuration


async def _wait_settled[T](task: asyncio.Task[T]) -> bool:
    """Wait until the task ends, however often a cancel arrives, and report whether one arrived.

    A cancel stops only the wait, never the task it waits for, so a second cancel cannot cut the task off either.
    """
    is_cancelled = False
    while not task.done():
        try:
            await asyncio.wait({task})
        except asyncio.CancelledError:
            is_cancelled = True
    return is_cancelled


async def _delete_queued_task(job: TaskJob, jobs: JobStore, configuration: Configuration) -> None:
    """Cancel a queued task, which bills nothing, and delete its record once ModelArk accepts.

    ModelArk refuses when the task started in the meantime. The person asked to stop, so the refusal is not raised,
    and the record stays: it is how the paid task's output is collected later.
    """
    try:
        await send_task_cancel(job.job_id, configuration)
    except ByteplusError:
        return
    else:
        await asyncio.to_thread(jobs.delete, job.job_id)


def _read_task_id(document: Json) -> str:
    """Read the new task's ID; the reply came with a success status, so a task may run even when it cannot be read."""
    try:
        reply = TaskCreateReply.model_validate(document)
    except ValidationError:
        raise ByteplusError(ErrorCode.UNCERTAIN, TASK_UNRECORDED) from None
    if TASK_ID.match(reply.id) is None:
        raise ByteplusError(ErrorCode.UNCERTAIN, TASK_UNRECORDED)
    return reply.id


def _parse_task_reply(document: Json) -> TaskReply:
    """Read a status check; a check bills nothing, so one that does not parse leaves the record for another."""
    try:
        return TaskReply.model_validate(document)
    except ValidationError:
        raise ByteplusError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None


def _build_ended_failure(job: TaskJob, reply: TaskReply) -> ByteplusError:
    """Build the error of a task that ended without files: failed, cancelled, or expired, none of which is billed.

    A failed task's code chooses its message, such as a moderation refusal, with ModelArk's cleaned reason.
    """
    if reply.status == "failed":
        error = reply.error
        return build_failure(None, error.code if error else None, error.message if error else "")
    outcome = "CANCELLED" if reply.status == "cancelled" else "EXPIRED"
    return ByteplusError(ErrorCode.UNAVAILABLE, TASK_OUTCOMES[job.kind][outcome])


class TaskDownloadOperation:
    """Wait for one recorded task and download what it made; status checks, cancels, and downloads bill nothing."""

    def __init__(self, job: TaskJob, jobs: JobStore, poll_seconds: int, last_status: str | None = None) -> None:
        """Keep the record, the store that deletes it, and the last status seen: queued right after the create request.

        A recorded task's status is unknown until the first check.
        """
        self.job = job
        self.jobs = jobs
        self.poll_seconds = poll_seconds
        self.last_status = last_status

    async def _wait_for_end(self, configuration: Configuration) -> TaskReply:
        """Check the task at once and then every poll interval, until it ends or the request timeout passes.

        At the timeout nothing is cancelled, since the task may still start, and the record stays for the Download node.
        """
        seconds = configuration.settings.request_timeout_seconds
        deadline = time.monotonic() + seconds
        url = TASK_URL.format(task_id=self.job.job_id)
        while True:
            reply = _parse_task_reply(await send_lookup(url, configuration))
            self.last_status = reply.status
            if reply.status in DONE_STATUSES:
                return reply
            if time.monotonic() >= deadline:
                message = TASK_OUTCOMES[self.job.kind]["WAIT_LIMIT"].format(seconds=seconds)
                raise ByteplusError(ErrorCode.TIMEOUT, message)
            await asyncio.sleep(self.poll_seconds)

    async def _download_outputs(self, reply: TaskReply, configuration: Configuration) -> dict[str, TaskOutput]:
        """Download each address the finished task holds once, in content field order, without the key."""
        content = reply.content.model_dump() if reply.content is not None else {}
        addresses: dict[str, str] = {field: content[field] for field in CONTENT_FIELDS if content.get(field)}
        if not addresses:
            raise ByteplusError(ErrorCode.TRANSPORT, REPLY_UNREADABLE)
        return {
            field: TaskOutput(address, await download_output(address, configuration.settings))
            for field, address in addresses.items()
        }

    def validate(self, settings: Settings) -> None:
        """Accept any recorded task; there is nothing to refuse before checking its status."""

    async def send(self, configuration: Configuration) -> TaskResult:
        """Wait for the task and download what it made, deleting the record once the task ends without files or saves.

        A cancel while the last status seen is queued cancels the task. A cancel while it runs, or before its status
        is known, sends nothing and keeps the record, since a started task runs on and is billed.
        """
        job = self.job
        if datetime.now(UTC) >= datetime.fromisoformat(job.submitted_at) + timedelta(seconds=TASK_RETENTION_SECONDS):
            await asyncio.to_thread(self.jobs.delete, job.job_id)
            raise ByteplusError(ErrorCode.UNAVAILABLE, TASK_GONE)
        try:
            reply = await self._wait_for_end(configuration)
        except asyncio.CancelledError:
            if self.last_status == CANCELLABLE_STATUS:
                await _wait_settled(asyncio.create_task(_delete_queued_task(job, self.jobs, configuration)))
            raise
        if reply.status != "succeeded":
            await asyncio.to_thread(self.jobs.delete, job.job_id)
            raise _build_ended_failure(job, reply)
        if time.time() >= reply.updated_at + OUTPUT_LIFETIME_SECONDS:
            await asyncio.to_thread(self.jobs.delete, job.job_id)
            raise ByteplusError(ErrorCode.UNAVAILABLE, TASK_FILES_EXPIRED)
        outputs = await self._download_outputs(reply, configuration)
        # The record goes only after every download, so a failed download can be collected again.
        await asyncio.to_thread(self.jobs.delete, job.job_id)
        return TaskResult(job, outputs, reply.created_at, reply.updated_at)


class TaskOperation[Row: ModelRow]:
    """One video or 3D task, sent once and recorded as soon as ModelArk accepts it."""

    def __init__(self, request: TaskRequest[Row], jobs: JobStore) -> None:
        """Keep the request to check and send, and the store its task is recorded in."""
        self.request = request
        self.jobs = jobs

    async def _create_job(self, body: Mapping[str, Json], configuration: Configuration) -> TaskJob:
        """Send the create request once, and record the task before anything waits for it."""
        request = self.request
        submitted_at = datetime.now(UTC).isoformat()
        job_id = _read_task_id(await send_json(ENDPOINT_URLS["tasks"], body, configuration))
        job = TaskJob(
            version=1,
            job_id=job_id,
            kind=request.kind,
            model_id=request.model_id,
            submitted_at=submitted_at,
            is_draft=request.is_draft,
        )
        await asyncio.to_thread(self.jobs.save, job)
        return job

    def validate(self, settings: Settings) -> None:
        """Run the checks of the task's kind that need no model row, the upload limit included."""
        self.request.validate_request(settings)

    async def send(self, configuration: Configuration) -> TaskResult:
        """Check the request against the model's row, create and record the task, and wait for it.

        A cancel during the create request waits for that request to end, so a task it created is recorded and then
        cancelled while it is still queued, rather than left running without a record.
        """
        request = self.request
        # find_model returns the row type of the kind it is given, which is the row type the request's checks take.
        match: ModelMatch[Row] = cast("ModelMatch[Row]", find_model(request.model_id, request.kind))
        body = request.build_body(match)
        creating = asyncio.create_task(self._create_job(body, configuration))
        is_cancelled = await _wait_settled(creating)
        job = creating.result()
        if is_cancelled:
            await _wait_settled(asyncio.create_task(_delete_queued_task(job, self.jobs, configuration)))
            raise asyncio.CancelledError
        download = TaskDownloadOperation(job, self.jobs, request.poll_seconds, last_status=CANCELLABLE_STATUS)
        return await download.send(configuration)


__all__ = ["TaskDownloadOperation", "TaskOperation"]
