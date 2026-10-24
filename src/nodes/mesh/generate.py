"""Make a GLB 3D model with Hyper3D or Hitem3D, from a prompt, images, or image references."""

from __future__ import annotations

import io as memory
from typing import TYPE_CHECKING, override

from comfy_api.latest import Types, io

from ..base import PaidNode
from ..inputs import REFERENCES_INPUT, encode_sized_images, build_request_inputs
from ...state.tasks import MeshRequest
from ...state.errors import ErrorCode, BytePlusError
from ...comfy.runtime import get_runtime
from ...byteplus.meshes import build_mesh_operation
from ...comfy.execution import send_request, wait_for_thread
from ...config.namespace import MENUS, NODE_PREFIX
from ...config.messages.run import REPLY_UNREADABLE
from ...config.messages.tasks import MESH_NOT_GLB
from ...config.generation.inputs import INPUT_NAMES, MODEL_TOOLTIP
from ...config.generation.meshes import FILE_FORMAT, GLB_SIGNATURE
from ...config.generation.models import DEFAULT_MODELS

if TYPE_CHECKING:
    import torch

    from ...state.tasks import TaskResult
    from ...state.options import Options
    from ...state.references import Reference


def build_mesh_output(result: TaskResult) -> io.NodeOutput:
    """Return the task's GLB file as ComfyUI's 3D file, kept in memory until Save 3D Model writes it.

    A task that holds no 3D file, or a file that is not GLB, ends the run, because no 3D node can open it.
    """
    output = result.outputs.get('file_url')
    if output is None:
        raise BytePlusError(ErrorCode.TRANSPORT, REPLY_UNREADABLE)
    if not output.content.startswith(GLB_SIGNATURE):
        raise BytePlusError(ErrorCode.TRANSPORT, MESH_NOT_GLB)
    return io.NodeOutput(Types.File3D(memory.BytesIO(output.content), FILE_FORMAT))


class MeshGenerate(PaidNode):
    """Create one 3D task, record it, wait for it, and return its GLB model."""

    list_inputs = frozenset({'images'})

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """List the model, the images and references, the run number, and the prompt with the model's commands."""
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='3D: Generate',
            category=MENUS['MESH'],
            description='Make a GLB 3D model with a ModelArk 3D model, from a prompt or images.',
            is_input_list=True,
            hidden=[io.Hidden.unique_id],
            inputs=[
                io.String.Input(INPUT_NAMES['MODEL'], default=DEFAULT_MODELS['meshes'], tooltip=MODEL_TOOLTIP),
                io.Image.Input(
                    'images',
                    optional=True,
                    tooltip=(
                        'Images of the subject: one, a batch, or a list. Hyper3D takes up to 5, image references '
                        'included; Hitem3D reads only addresses, so connect references instead.'
                    ),
                ),
                REFERENCES_INPUT,
                *build_request_inputs(),
                io.String.Input(
                    'prompt',
                    multiline=True,
                    default='',
                    tooltip=(
                        "What to make, in English, for Hyper3D, then any of the model's commands, such as --material "
                        'PBR. It may be empty when images or image references are connected.'
                    ),
                ),
            ],
            outputs=[io.File3DGLB.Output('model_3d', display_name='model_3d')],
        )

    @classmethod
    @override
    async def send(
        cls,
        *,
        model: str,
        images: list[torch.Tensor] | None = None,
        references: tuple[Reference, ...] | None = None,
        options: Options | None = None,
        prompt: str,
    ) -> io.NodeOutput:
        """Encode the images in a worker thread, then create, record, and wait for the task."""
        encoded = await wait_for_thread(lambda: encode_sized_images(images or ()))
        request = MeshRequest(
            model_id=model.strip(),
            prompt=prompt.strip(),
            images=encoded,
            references=references or (),
            options=options,
        )
        operation = build_mesh_operation(request, get_runtime().tasks)
        return await send_request(
            operation.request.validate_request, operation.send, build_mesh_output, cls.hidden.unique_id
        )


__all__ = ['MeshGenerate', 'build_mesh_output']
