"""Collect a recorded video task that kept running after a cancel, a restart, or a timeout."""

from __future__ import annotations

import asyncio
from typing import override
from comfy_api.latest import io
from ...comfy.runtime import get_runtime
from .generate import build_video_outputs
from ...types.errors import ErrorCode, ByteplusError
from ...comfy.execution import send_request, wait_for_task
from ...byteplus.tasks.jobs import TASK_ID, list_job_labels
from ...byteplus.tasks.operation import TaskDownloadOperation
from ...config.generation.videos import POLL_INTERVAL_SECONDS
from ...config.messages.tasks import JOB_UNKNOWN, VIDEO_JOB_KIND
from ...config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES


class VideoDownload(io.ComfyNode):
    """Wait for one recorded video task and return its video, last frame, and references.

    Collecting a task sends only status checks, a cancel of a queued task, and downloads, which bill nothing, and the
    same task always gives the same outputs, so ComfyUI's cache is correct and this is not a paid node.
    """

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the recorded video tasks when ComfyUI builds the node definitions; the R key reads them again."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Video: Download",
            category=MENUS["VIDEO"],
            description="Collect a video task that kept running after a cancel, a restart, or a timeout.",
            inputs=[
                io.Combo.Input(
                    "job",
                    options=list_job_labels(get_runtime().jobs, "videos"),
                    tooltip="A video task recorded on this server. Press R to list tasks recorded later.",
                )
            ],
            outputs=[
                io.Video.Output("video", display_name="video"),
                io.Image.Output("last_frame", display_name="last_frame"),
                io.Custom(SOCKET_TYPES["REFERENCES"]).Output("references", display_name="references"),
            ],
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    def validate_inputs(cls, **inputs: object) -> bool | str:
        """Take a task recorded after the node definitions were built, as long as the label starts with a task ID.

        ComfyUI skips its own list check only for inputs the validator takes as positional or extra keywords.
        """
        return True if TASK_ID.match(str(inputs.get("job", "")).split(" ", 1)[0]) else JOB_UNKNOWN

    @classmethod
    @override
    async def execute(cls, *, job: str = "") -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        """Read the task's record, wait for it, and download what it made."""
        jobs = get_runtime().jobs
        record = await asyncio.to_thread(jobs.read, job.split(" ", 1)[0])
        if record.kind != "videos":
            raise ByteplusError(ErrorCode.INVALID_INPUT, VIDEO_JOB_KIND)
        operation = TaskDownloadOperation(record, jobs, POLL_INTERVAL_SECONDS)
        return await wait_for_task(
            asyncio.create_task(send_request(operation, build_video_outputs, cls.hidden.unique_id))
        )


__all__ = ["VideoDownload"]
