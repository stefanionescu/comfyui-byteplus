"""Create a video or 3D task and record it as soon as ModelArk accepts it, then wait for it and download what it made.

When the person cancels a run while its task waits in the queue, ModelArk cancels the task and bills nothing. A task
that started runs on, and its record stays.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING
import asyncio
from datetime import UTC, datetime, timedelta
from dataclasses import dataclass

from pydantic import ValidationError

from .records import TASK_ID
from ..failures import build_failure
from ..transport import send_json, send_lookup, download_output, send_task_cancel
from ...state.tasks import TaskRecord, TaskResult
from ...state.errors import ErrorCode, BytePlusError
from ...config.models import KIND_NODES
from ...state.replies import TaskReply, TaskCreateReply
from ...config.byteplus import ENDPOINT_URLS
from ...state.references import OutputFile
from ...config.messages.run import REPLY_UNREADABLE
from ...config.messages.tasks import (
    TASK_GONE,
    TASK_NAMES,
    TASK_EXPIRED,
    DOWNLOAD_NODES,
    TASK_CANCELLED,
    TASK_UNRECORDED,
    TASK_WAIT_LIMIT,
    TASK_FILES_EXPIRED,
)
from ...config.generation.videos import (
    DONE_STATUSES,
    CANCELLABLE_STATUS,
    POLL_INTERVAL_SECONDS,
    TASK_RETENTION_SECONDS,
)
from ...config.generation.references import OUTPUT_LIFETIME_SECONDS

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ...state import Json
    from .records import TaskStore
    from ...state.tasks import TaskRequest
    from ...state.settings import Configuration


async def _wait_settled[T](task: asyncio.Task[T]) -> bool:
    """Wait until the asyncio task ends, however often a cancel arrives, and report whether one arrived.

    A cancel stops only the wait, never the asyncio task it waits for, so a second cancel cannot cut it off either.
    """
    is_cancelled = False
    while not task.done():
        try:
            await asyncio.wait({task})
        except asyncio.CancelledError:
            is_cancelled = True
    return is_cancelled


async def _send_cancel(record: TaskRecord, tasks: TaskStore, configuration: Configuration) -> None:
    """Cancel a queued task, which bills nothing, and delete its record once ModelArk accepts.

    ModelArk refuses when the task started in the meantime. The person asked to stop, so this function does not raise
    the refusal. The record stays, because it lets a later run collect the output of the paid task.
    """
    try:
        await send_task_cancel(record.task_id, configuration)
    except BytePlusError:
        return
    else:
        await asyncio.to_thread(tasks.delete, record.task_id)


def _read_task_id(document: Json) -> str:
    """Read the new task ID; the reply had a success status, so a task may run even when the reply is unreadable."""
    try:
        reply = TaskCreateReply.model_validate(document)
    except ValidationError:
        raise BytePlusError(ErrorCode.UNCERTAIN, TASK_UNRECORDED) from None
    if TASK_ID.match(reply.id) is None:
        raise BytePlusError(ErrorCode.UNCERTAIN, TASK_UNRECORDED)
    return reply.id


def _parse_task_reply(document: Json) -> TaskReply:
    """Read the reply of a status check.

    A check bills nothing, so an unreadable reply is a transport error, and the record stays for a later check.
    """
    try:
        return TaskReply.model_validate(document)
    except ValidationError:
        raise BytePlusError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None


def _build_ended_failure(record: TaskRecord, reply: TaskReply) -> BytePlusError:
    """Build the error of a task that ended without files, which ModelArk does not bill: failed, cancelled, or expired.

    The code of a failed task chooses its message, such as a moderation refusal, with the cleaned reason from ModelArk.
    """
    if reply.status == 'failed':
        error = reply.error
        return build_failure(None, error.code if error else None, error.message if error else '')
    template = TASK_CANCELLED if reply.status == 'cancelled' else TASK_EXPIRED
    return BytePlusError(
        ErrorCode.UNAVAILABLE, template.format(task=TASK_NAMES[record.kind], node=KIND_NODES[record.kind])
    )


class TaskDownloadOperation:
    """Wait for one recorded task and download what it made; status checks, cancels, and downloads bill nothing."""

    def __init__(self, record: TaskRecord, tasks: TaskStore, last_status: str | None = None) -> None:
        """Keep the record, the store that deletes it, and the last status seen.

        The last status is `queued` right after the create request, and `None` for a recorded task before its first
        check.
        """
        self.record = record
        self.tasks = tasks
        self.last_status = last_status

    async def _wait_for_end(self, configuration: Configuration) -> TaskReply:
        """Check the task at once and then every poll interval until it ends or the request timeout passes.

        At the timeout this method cancels nothing, because the task may still start, and the record stays for the
        Download node.
        """
        seconds = configuration.settings.request_timeout_seconds
        deadline = time.monotonic() + seconds
        url = f'{ENDPOINT_URLS["tasks"]}/{self.record.task_id}'
        while True:
            reply = _parse_task_reply(await send_lookup(url, configuration))
            self.last_status = reply.status
            if reply.status in DONE_STATUSES:
                return reply
            if time.monotonic() >= deadline:
                kind = self.record.kind
                message = TASK_WAIT_LIMIT.format(task=TASK_NAMES[kind], seconds=seconds, node=DOWNLOAD_NODES[kind])
                raise BytePlusError(ErrorCode.TIMEOUT, message)
            await asyncio.sleep(POLL_INTERVAL_SECONDS)

    async def _download_outputs(self, reply: TaskReply, configuration: Configuration) -> dict[str, OutputFile]:
        """Download each address the finished task holds once, in reply field order, without the key."""
        content: dict[str, str | None] = reply.content.model_dump() if reply.content is not None else {}
        addresses = {field: address for field, address in content.items() if address}
        if not addresses:
            raise BytePlusError(ErrorCode.TRANSPORT, REPLY_UNREADABLE)
        return {
            field: OutputFile(await download_output(address, configuration.settings), address)
            for field, address in addresses.items()
        }

    async def send(self, configuration: Configuration) -> TaskResult:
        """Wait for the task, download what it made, and delete the record once nothing remains to collect.

        A cancel while the last status seen is `queued` cancels the task. A cancel sends nothing and keeps the record
        while the task runs or before its first status check. A started task runs on, and ModelArk bills it.
        """
        record = self.record
        if datetime.now(UTC) >= datetime.fromisoformat(record.submitted_at) + timedelta(seconds=TASK_RETENTION_SECONDS):
            await asyncio.to_thread(self.tasks.delete, record.task_id)
            raise BytePlusError(ErrorCode.UNAVAILABLE, TASK_GONE.format(node=KIND_NODES[record.kind]))
        try:
            reply = await self._wait_for_end(configuration)
        except asyncio.CancelledError:
            if self.last_status == CANCELLABLE_STATUS:
                await _wait_settled(asyncio.create_task(_send_cancel(record, self.tasks, configuration)))
            raise
        if reply.status != 'succeeded':
            await asyncio.to_thread(self.tasks.delete, record.task_id)
            raise _build_ended_failure(record, reply)
        if time.time() >= reply.updated_at + OUTPUT_LIFETIME_SECONDS:
            await asyncio.to_thread(self.tasks.delete, record.task_id)
            raise BytePlusError(ErrorCode.UNAVAILABLE, TASK_FILES_EXPIRED)
        outputs = await self._download_outputs(reply, configuration)
        # The record goes only after every download, so a later run can collect a failed download again.
        await asyncio.to_thread(self.tasks.delete, record.task_id)
        return TaskResult(record, outputs, reply.created_at)


@dataclass(frozen=True, slots=True)
class TaskOperation:
    """One video or 3D task, sent once and recorded as soon as ModelArk accepts it.

    Attributes:
        request: The request to check and send; its validate_request runs the checks of its kind that need no model
            row, the upload limit included.
        tasks: The store that records the task.

    """

    request: TaskRequest
    tasks: TaskStore

    async def _create_record(self, body: Mapping[str, Json], configuration: Configuration) -> TaskRecord:
        """Send the create request once, and record the task before anything waits for it."""
        request = self.request
        submitted_at = datetime.now(UTC).isoformat()
        task_id = _read_task_id(await send_json(ENDPOINT_URLS['tasks'], body, configuration))
        record = TaskRecord(
            version=1,
            task_id=task_id,
            kind=request.kind,
            model_id=request.model_id,
            submitted_at=submitted_at,
            is_draft=request.is_draft,
        )
        await asyncio.to_thread(self.tasks.save, record)
        return record

    async def send(self, configuration: Configuration) -> TaskResult:
        """Check the request against the model row, create and record the task, and wait for it.

        A cancel during the create request waits for that request to end. The method then records a task that the
        request created and cancels it while it still waits in the queue, so no task runs without a record.
        """
        body = self.request.build_body()
        creating = asyncio.create_task(self._create_record(body, configuration))
        is_cancelled = await _wait_settled(creating)
        record = creating.result()
        if is_cancelled:
            await _wait_settled(asyncio.create_task(_send_cancel(record, self.tasks, configuration)))
            raise asyncio.CancelledError
        return await TaskDownloadOperation(record, self.tasks, last_status=CANCELLABLE_STATUS).send(configuration)


__all__ = ['TaskDownloadOperation', 'TaskOperation']
