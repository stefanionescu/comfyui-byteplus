"""Collect a recorded video or 3D task that kept running after a cancel, a restart, or a timeout."""

from __future__ import annotations

from typing import override

from comfy_api.latest import io

from .base import TaskDownload
from .inputs import REFERENCES_OUTPUT
from .mesh.generate import build_mesh_output
from ..comfy.runtime import get_runtime
from .video.generate import build_video_outputs
from ..config.namespace import MENUS, NODE_PREFIX
from ..byteplus.tasks.records import list_task_labels


class VideoDownload(TaskDownload):
    """Wait for one recorded video task and return its video, last frame, and references."""

    kind = 'videos'
    build_outputs = staticmethod(build_video_outputs)

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """List the recorded video tasks when ComfyUI builds the node definitions; the R key reads them again."""
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='Video: Download',
            category=MENUS['VIDEO'],
            description='Collect a video task that kept running after a cancel, a restart, or a timeout.',
            inputs=[
                io.Combo.Input(
                    'task',
                    options=list_task_labels(get_runtime().tasks, cls.kind),
                    tooltip='A video task recorded on this server. Press R to list tasks recorded later.',
                )
            ],
            outputs=[
                io.Video.Output('video', display_name='video'),
                io.Image.Output('last_frame', display_name='last_frame'),
                REFERENCES_OUTPUT,
            ],
            hidden=[io.Hidden.unique_id],
        )


class MeshDownload(TaskDownload):
    """Wait for one recorded 3D task and return its GLB model."""

    kind = 'meshes'
    build_outputs = staticmethod(build_mesh_output)

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """List the recorded 3D tasks when ComfyUI builds the node definitions; the R key reads them again."""
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='3D: Download',
            category=MENUS['MESH'],
            description='Collect a 3D task that kept running after a cancel, a restart, or a timeout.',
            inputs=[
                io.Combo.Input(
                    'task',
                    options=list_task_labels(get_runtime().tasks, cls.kind),
                    tooltip='A 3D task recorded on this server. Press R to list tasks recorded later.',
                )
            ],
            outputs=[io.File3DGLB.Output('model_3d', display_name='model_3d')],
            hidden=[io.Hidden.unique_id],
        )


__all__ = ['MeshDownload', 'VideoDownload']
