"""Collect a recorded 3D task that kept running after a cancel, a restart, or a timeout."""

from __future__ import annotations

import asyncio
from typing import override
from comfy_api.latest import io
from .generate import build_mesh_output
from ...comfy.runtime import get_runtime
from ...config.namespace import MENUS, NODE_PREFIX
from ...types.errors import ErrorCode, ByteplusError
from ...comfy.execution import send_request, wait_for_task
from ...byteplus.tasks.jobs import TASK_ID, list_job_labels
from ...byteplus.tasks.operation import TaskDownloadOperation
from ...config.messages.tasks import JOB_UNKNOWN, MESH_JOB_KIND
from ...config.generation.meshes import JOB_KIND, POLL_INTERVAL_SECONDS


class MeshDownload(io.ComfyNode):
    """Wait for one recorded 3D task and return its GLB model.

    Collecting a task sends only status checks, a cancel of a queued task, and downloads, which bill nothing, and the
    same task always gives the same file, so ComfyUI's cache is correct and this is not a paid node.
    """

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the recorded 3D tasks when ComfyUI builds the node definitions; the R key reads them again."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="3D: Download",
            category=MENUS["MESH"],
            description="Collect a 3D task that kept running after a cancel, a restart, or a timeout.",
            inputs=[
                io.Combo.Input(
                    "job",
                    options=list_job_labels(get_runtime().jobs, JOB_KIND),
                    tooltip="A 3D task recorded on this server. Press R to list tasks recorded later.",
                )
            ],
            outputs=[io.File3DGLB.Output("model_3d", display_name="model_3d")],
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
        """Read the task's record, wait for it, and download its 3D file."""
        jobs = get_runtime().jobs
        record = await asyncio.to_thread(jobs.read, job.split(" ", 1)[0])
        if record.kind != JOB_KIND:
            raise ByteplusError(ErrorCode.INVALID_INPUT, MESH_JOB_KIND)
        operation = TaskDownloadOperation(record, jobs, POLL_INTERVAL_SECONDS)
        return await wait_for_task(
            asyncio.create_task(send_request(operation, build_mesh_output, cls.hidden.unique_id))
        )


__all__ = ["MeshDownload"]
