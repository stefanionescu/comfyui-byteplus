"""Collect a recorded video task that kept running after a cancel, a restart, or a timeout."""

from __future__ import annotations

from ..base import TaskDownload
from comfy_api.latest import io
from ...comfy.runtime import get_runtime
from .generate import build_video_outputs
from ...byteplus.tasks.records import list_task_labels
from ...config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES


class VideoDownload(TaskDownload):
    """Wait for one recorded video task and return its video, last frame, and references."""

    kind = "videos"
    build_outputs = staticmethod(build_video_outputs)

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
                    "task",
                    options=list_task_labels(get_runtime().tasks, cls.kind),
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


__all__ = ["VideoDownload"]
