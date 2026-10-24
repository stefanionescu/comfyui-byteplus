"""Run requests with ComfyUI's progress bar and its cancel."""

from __future__ import annotations

from typing import TYPE_CHECKING
import asyncio

from comfy_api.latest import ComfyAPI
from comfy.model_management import InterruptProcessingException, throw_exception_if_processing_interrupted

from .runtime import get_runtime
from ..state.errors import ErrorCode, BytePlusError
from ..config.byteplus import CONSOLE_URLS
from ..config.execution import PROGRESS_STEPS, CANCELLATION_POLL_SECONDS
from ..config.messages.run import REQUEST_TIMEOUT

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from comfy_api.latest import io

    from ..state.settings import Settings, Configuration


async def _wait_shielded[T](task: asyncio.Task[T]) -> bool:
    """Wait until the task settles despite cancellation, and report whether cancellation arrived."""
    cancelled = False
    while not task.done():
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            cancelled = True
        except Exception:  # noqa: BLE001 # reason: The caller reads the settled task's failure after resolving cancellation.
            break
    return cancelled


async def wait_for_thread[T](work: Callable[[], T]) -> T:
    """Run blocking work in a thread, and finish it before letting a cancel through."""
    task = asyncio.create_task(asyncio.to_thread(work))
    if await _wait_shielded(task):
        task.exception()
        raise asyncio.CancelledError
    return task.result()


async def wait_for_task[T](task: asyncio.Task[T]) -> T:
    """Forward ComfyUI interruption to the owned preparation or execution task."""
    try:
        while not task.done():
            throw_exception_if_processing_interrupted()
            await asyncio.wait({task}, timeout=CANCELLATION_POLL_SECONDS)
        return await task
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)


async def send_request[Result](
    validate: Callable[[Settings], None],
    send: Callable[[Configuration], Coroutine[object, object, Result]],
    build_outputs: Callable[[Result], io.NodeOutput],
    node_id: str | None,
) -> io.NodeOutput:
    """Validate, send, and build the outputs of the node, showing only the progress bar of ComfyUI.

    `validate` refuses inputs that the settings or the endpoint do not allow, before the node sends anything; `send`
    sends the paid request and returns its parsed result. The bar belongs to the node: a node that another node calls
    has no ID, so it leaves the bar of the calling node alone. Building the outputs decodes media, which blocks, so it
    runs in a worker thread.
    """
    progress = ComfyAPI().execution
    if node_id is not None:
        await progress.set_progress(0, PROGRESS_STEPS, node_id=node_id)
    configuration = await asyncio.to_thread(get_runtime().configuration.read_configuration)
    validate(configuration.settings)
    if node_id is not None:
        await progress.set_progress(1, PROGRESS_STEPS, node_id=node_id)
    try:
        result = await wait_for_task(asyncio.create_task(send(configuration)))
        if node_id is not None:
            await progress.set_progress(2, PROGRESS_STEPS, node_id=node_id)
        outputs = await wait_for_thread(lambda: build_outputs(result))
        if node_id is not None:
            await progress.set_progress(PROGRESS_STEPS, PROGRESS_STEPS, node_id=node_id)
    except BytePlusError as error:
        if error.code is ErrorCode.INTERRUPTED:
            raise InterruptProcessingException from None
        raise
    except TimeoutError:
        seconds = configuration.settings.request_timeout_seconds
        raise BytePlusError(ErrorCode.TIMEOUT, REQUEST_TIMEOUT.format(seconds=seconds, **CONSOLE_URLS)) from None
    return outputs


__all__ = ['send_request', 'wait_for_task', 'wait_for_thread']
