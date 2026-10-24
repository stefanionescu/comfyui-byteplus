"""Share the paid nodes' cache key, run number, list inputs, and dropdowns, and the Download nodes' collection."""

from __future__ import annotations

import asyncio
from comfy_api.latest import io
from ..comfy.runtime import get_runtime
from ..byteplus.tasks.records import TASK_ID
from ..config.messages.inputs import SINGLE_VALUE
from ..types.errors import ErrorCode, BytePlusError
from ..comfy.execution import send_request, wait_for_task
from ..byteplus.tasks.operation import TaskDownloadOperation
from ..config.generation.inputs import INPUT_NAMES, VALUE_CHOICE
from typing import cast, Literal, ClassVar, override, TYPE_CHECKING
from ..config.messages.tasks import TASK_KIND, TASK_NAMES, TASK_UNKNOWN, DOWNLOAD_NODES

if TYPE_CHECKING:
    from ..types.tasks import TaskResult
    from collections.abc import Callable, Awaitable


class PaidNode(io.ComfyNode):
    """Own the cache key and the run-number input every paid node shares.

    Attributes:
        send: Typed entry point that receives every saved input except the run number.
        list_inputs: The media inputs of a node that takes input lists; each reaches send as the whole list, and
            every other input as its one value.
        choice_inputs: The default or custom dropdowns; each reaches send as its custom value, or None at default.

    """

    send: ClassVar[Callable[..., Awaitable[io.NodeOutput]]]
    list_inputs: ClassVar[frozenset[str]] = frozenset()
    choice_inputs: ClassVar[frozenset[str]] = frozenset()

    @classmethod
    async def fingerprint_inputs(cls, **_inputs: object) -> str:
        """Add the API key's token to the cache key, so a new key runs the node again."""
        snapshot = await asyncio.to_thread(get_runtime().configuration.read_snapshot)
        return snapshot.generation

    @classmethod
    async def execute(cls, **inputs: object) -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI awaits an async execute.
        """Drop the run number, which ComfyUI uses to invalidate its cache, and send.

        A node that takes input lists receives every input as a list; only its media inputs may hold several items.
        """
        inputs.pop(INPUT_NAMES["RUN_NUMBER"], None)
        if cls.list_inputs:
            for name, value in inputs.items():
                if name not in cls.list_inputs:
                    inputs[name] = _read_single(name, value)
        for name in cls.choice_inputs & inputs.keys():
            choice = cast("dict[str, object]", inputs[name])
            inputs[name] = choice[VALUE_CHOICE["VALUE"]] if choice[name] == VALUE_CHOICE["SET"] else None
        return await cls.send(**inputs)


class TaskDownload(io.ComfyNode):
    """Wait for one recorded task of the node's kind and return what it made.

    Collecting a task bills nothing: it sends only status checks, downloads, and a cancel of a queued task. The same
    task always gives the same outputs, so ComfyUI's cache is correct and this is not a paid node.

    Attributes:
        kind: The kind of task the node lists and collects.
        build_outputs: Builds the node's outputs from what the task made.

    """

    kind: ClassVar[Literal["videos", "meshes"]]
    build_outputs: ClassVar[Callable[[TaskResult], io.NodeOutput]]

    @classmethod
    @override
    def validate_inputs(cls, **inputs: object) -> bool | str:
        """Take a task recorded after the node definitions were built, as long as the label starts with a task ID.

        ComfyUI skips its own list check only for inputs the validator takes as positional or extra keywords.
        """
        return True if TASK_ID.match(str(inputs.get("task", "")).split(" ", 1)[0]) else TASK_UNKNOWN

    @classmethod
    @override
    async def execute(cls, *, task: str = "") -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        """Read the task's record, wait for it, and download what it made."""
        tasks = get_runtime().tasks
        record = await asyncio.to_thread(tasks.read, task.split(" ", 1)[0])
        if record.kind != cls.kind:
            message = TASK_KIND.format(task=TASK_NAMES[record.kind], node=DOWNLOAD_NODES[record.kind])
            raise BytePlusError(ErrorCode.INVALID_INPUT, message)
        operation = TaskDownloadOperation(record, tasks)
        return await wait_for_task(
            asyncio.create_task(send_request(operation, cls.build_outputs, cls.hidden.unique_id))
        )


def _read_single(name: str, value: object) -> object:
    """Take the one value an input list holds; a dynamic dropdown holds one list for each of its fields."""
    if isinstance(value, dict):
        fields = cast("dict[str, object]", value)
        return {field: _read_single(name, item) for field, item in fields.items()}
    values = cast("list[object]", value)
    if len(values) != 1:
        raise BytePlusError(ErrorCode.INVALID_INPUT, SINGLE_VALUE.format(name=name))
    return values[0]


__all__ = ["PaidNode", "TaskDownload"]
