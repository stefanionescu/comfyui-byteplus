"""Make a GLB 3D model with Hyper3D or Hitem3D, from a prompt, images, or image references."""

from __future__ import annotations

import asyncio
import io as memory
from ..base import PaidNode
from functools import partial
from typing import TYPE_CHECKING
from ...types.tasks import TaskRequest
from comfy_api.latest import io, Types
from ...types.meshes import MeshRequest
from ...comfy.runtime import get_runtime
from ...config.messages.tasks import MESH_NOT_GLB
from ...config.namespace import MENUS, NODE_PREFIX
from ...config.messages.run import REPLY_UNREADABLE
from ...types.errors import ErrorCode, ByteplusError
from ...byteplus.tasks.operation import TaskOperation
from ...config.generation.models import DEFAULT_MODELS
from ...byteplus.meshes import build_mesh_body, validate_mesh_request
from ...comfy.execution import send_request, wait_for_task, wait_for_thread
from ..inputs import REFERENCES_INPUT, encode_sized_images, build_request_inputs
from ...config.generation.inputs import INPUT_NAMES, MODEL_DEFAULT, MODEL_TOOLTIP
from ...config.generation.meshes import (
    POSES,
    JOB_KIND,
    TEXTURES,
    MAX_FACES,
    PRECISIONS,
    TOPOLOGIES,
    FILE_FORMAT,
    GLB_SIGNATURE,
    VIEW_SEPARATOR,
    POLL_INTERVAL_SECONDS,
)

if TYPE_CHECKING:
    import torch
    from ...types.options import Options
    from ...types.tasks import TaskResult
    from ...types.references import Reference

# The 3D controls; a dropdown left at model default and faces at 0 send nothing.
_CONTROLS = (
    io.Combo.Input(
        "texture",
        options=list(TEXTURES),
        default=MODEL_DEFAULT,
        tooltip=(
            "White has no texture; textured bakes the lighting in; PBR adds metal and roughness maps for relighting."
        ),
    ),
    io.Combo.Input(
        "topology",
        display_name="mesh",
        options=list(TOPOLOGIES),
        default=MODEL_DEFAULT,
        advanced=True,
        tooltip="The mesh's faces, for Hyper3D: triangles, or quads for editing.",
    ),
    io.Int.Input(
        "faces",
        default=0,
        min=0,
        max=MAX_FACES,
        advanced=True,
        tooltip="The number of faces; 0 leaves it to the model.",
    ),
    io.Combo.Input(
        "precision",
        options=list(PRECISIONS),
        default=MODEL_DEFAULT,
        advanced=True,
        tooltip="Hitem3D's detail level; high costs more.",
    ),
    io.Combo.Input(
        "pose",
        options=list(POSES),
        default=MODEL_DEFAULT,
        advanced=True,
        tooltip="For Hyper3D characters: a standing pose ready for rigging.",
    ),
    io.String.Input(
        "views",
        default="",
        advanced=True,
        tooltip=(
            "For Hitem3D: the side each image shows, in order, such as front, left. Leave empty to let the model "
            "decide."
        ),
    ),
)


def build_mesh_output(result: TaskResult) -> io.NodeOutput:
    """Return the task's GLB file as ComfyUI's 3D file, kept in memory until Save 3D Model writes it.

    A task that holds no 3D file, or a file that is not GLB, ends the run, since no 3D node could open it.
    """
    output = result.outputs.get("file_url")
    if output is None:
        raise ByteplusError(ErrorCode.TRANSPORT, REPLY_UNREADABLE)
    if not output.content.startswith(GLB_SIGNATURE):
        raise ByteplusError(ErrorCode.TRANSPORT, MESH_NOT_GLB)
    return io.NodeOutput(Types.File3D(memory.BytesIO(output.content), FILE_FORMAT))


class MeshGenerate(PaidNode):
    """Create one 3D task, record it, wait for it, and return its GLB model."""

    list_inputs = frozenset({"images"})

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the model, the images and references, the 3D controls, the run number, and the prompt."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="3D: Generate",
            category=MENUS["MESH"],
            description="Make a GLB 3D model with a ModelArk 3D model, from a prompt or images.",
            inputs=[
                io.String.Input(INPUT_NAMES["MODEL"], default=DEFAULT_MODELS["meshes"], tooltip=MODEL_TOOLTIP),
                io.Image.Input(
                    "images",
                    optional=True,
                    tooltip=(
                        "Images of the subject: one, a batch, or a list. Hyper3D takes up to 5; Hitem3D needs "
                        "references instead."
                    ),
                ),
                REFERENCES_INPUT,
                *_CONTROLS,
                *build_request_inputs(has_seed=False),
                io.String.Input(
                    "prompt",
                    multiline=True,
                    default="",
                    placeholder="prompt",
                    tooltip="What to make, in English, for Hyper3D. It may be empty when images are connected.",
                ),
            ],
            outputs=[io.File3DGLB.Output("model_3d", display_name="model_3d")],
            is_input_list=True,
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    async def send(  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        prompt: str,
        model: str,
        texture: str,
        topology: str,
        faces: int,
        precision: str,
        pose: str,
        views: str,
        images: list[torch.Tensor] | None = None,
        references: tuple[Reference, ...] | None = None,
        options: Options | None = None,
    ) -> io.NodeOutput:
        """Encode the images inside the owned task, then create, record, and wait for the task."""
        sides = tuple(side.strip().lower() for side in views.split(VIEW_SEPARATOR) if side.strip())

        async def send_encoded() -> io.NodeOutput:
            """Encode the images inside the owned task, then send the request."""
            encoded = await wait_for_thread(lambda: encode_sized_images(images or ()))
            # A dropdown left at model default sends nothing.
            request = MeshRequest(
                model_id=model.strip(),
                prompt=prompt.strip(),
                images=encoded,
                references=references or (),
                texture=None if texture == MODEL_DEFAULT else texture,
                topology=None if topology == MODEL_DEFAULT else topology,
                faces=faces,
                precision=None if precision == MODEL_DEFAULT else precision,
                pose=None if pose == MODEL_DEFAULT else pose,
                views=sides,
                options=options,
            )
            task_request = TaskRequest(
                kind=JOB_KIND,
                model_id=request.model_id,
                validate_request=partial(validate_mesh_request, request),
                build_body=partial(build_mesh_body, request),
                is_draft=False,
                poll_seconds=POLL_INTERVAL_SECONDS,
            )
            operation = TaskOperation(task_request, get_runtime().jobs)
            return await send_request(operation, build_mesh_output, cls.hidden.unique_id)

        return await wait_for_task(asyncio.create_task(send_encoded()))


__all__ = ["MeshGenerate", "build_mesh_output"]
