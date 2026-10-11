"""Check a 3D request against what every 3D model and its own row take, build the task body, and build its task.

Hyper3D and Hitem3D read their settings as --name value commands after the prompt. The person writes them in the
prompt; the node only asks for GLB, the file its model_3d output carries.
"""

from __future__ import annotations

import re
from functools import partial
from .models import find_model
from typing import TYPE_CHECKING
from ..types.tasks import TaskRequest
from .options import build_request_body
from .tasks.operation import TaskOperation
from .operation import validate_upload_size
from .references import validate_references
from ..types.errors import ErrorCode, ByteplusError
from ..config.patterns import MESH_FORMAT_COMMAND_PATTERN
from ..config.messages.inputs import (
    MESH_INPUT_EMPTY,
    MESH_PROMPT_LENGTH,
    MESH_FORMAT_COMMAND,
    MESH_IMAGE_REQUIRED,
)

if TYPE_CHECKING:
    from ..types import Json
    from .tasks.jobs import JobStore
    from ..types.settings import Settings
    from ..types.meshes import MeshRequest

_FORMAT_COMMAND = re.compile(MESH_FORMAT_COMMAND_PATTERN, re.IGNORECASE)


def _build_text(request: MeshRequest, command: str) -> str:
    """Write the text item: the prompt as written, then the GLB format command unless the prompt already asks for GLB.

    The command's last word is the value that names GLB. A prompt that asks for another format is refused, since the
    node returns the file as GLB.
    """
    glb = command.rsplit(" ", 1)[-1]
    values = [value.lower() for value in _FORMAT_COMMAND.findall(request.prompt)]
    other = next((value for value in values if value != glb), None)
    if other is not None:
        raise ByteplusError(ErrorCode.INVALID_INPUT, MESH_FORMAT_COMMAND.format(value=other, command=command))
    if values:
        return request.prompt
    return " ".join(word for word in (request.prompt, command) if word)


def _validate_mesh_request(request: MeshRequest, settings: Settings) -> None:
    """Refuse, before the model row is read, a request no 3D model could take, and images over the upload limit.

    ModelArk reads image references itself, so only outputs and links are taken, and an output must not expire before
    the task starts.
    """
    if not request.prompt and not request.images and not request.references:
        raise ByteplusError(ErrorCode.INVALID_INPUT, MESH_INPUT_EMPTY)
    validate_upload_size([image.url for image in request.images], settings)
    validate_references(request.references, ("image",), can_read_assets=False)


def _build_mesh_body(request: MeshRequest) -> dict[str, Json]:
    """Refuse, before anything is paid, what the model's row does not take, then build the body with Request Options.

    A model that reads no text, such as Hitem3D, takes its commands in the text item but still needs an image to work
    from. The text item comes first, then the images, then the image references. ModelArk cuts a longer text without
    an error, which could drop the format command the node adds, so a prompt that leaves it too little room is refused.
    """
    match = find_model(request.model_id, "meshes")
    if not request.images and not request.references and "text" not in match.row.inputs:
        raise ByteplusError(ErrorCode.INVALID_INPUT, MESH_IMAGE_REQUIRED.format(model=match.model_id))
    limits = match.row.mesh
    text = _build_text(request, limits.format_command)
    if 0 < limits.max_prompt_characters < len(text):
        # The prompt is what the text holds beyond the added command and the space before it.
        maximum = limits.max_prompt_characters - (len(text) - len(request.prompt))
        raise ByteplusError(ErrorCode.INVALID_INPUT, MESH_PROMPT_LENGTH.format(model=match.model_id, maximum=maximum))
    content: list[Json] = [{"type": "text", "text": text}]
    content.extend({"type": "image_url", "image_url": {"url": image.url}} for image in request.images)
    content.extend({"type": "image_url", "image_url": {"url": reference.address}} for reference in request.references)
    return build_request_body({"model": match.model_id, "content": content}, request.options, "meshes", match.row)


def build_mesh_operation(request: MeshRequest, jobs: JobStore) -> TaskOperation:
    """Build the task that checks the 3D request, sends it, and records it."""
    validate_request = partial(_validate_mesh_request, request)
    build_body = partial(_build_mesh_body, request)
    return TaskOperation(TaskRequest("meshes", request.model_id, validate_request, build_body, is_draft=False), jobs)


__all__ = ["build_mesh_operation"]
