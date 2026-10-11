"""Check a 3D request against what every 3D model and its own row take, and build the task body.

Hyper3D and Hitem3D read their settings as --name value commands after the prompt. The person writes them in the
prompt; the node only asks for GLB, the file its model_3d output carries.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from datetime import UTC, datetime
from .options import build_request_body
from .operation import validate_upload_size
from .references import validate_references
from ..types.errors import ErrorCode, ByteplusError
from ..config.patterns import MESH_FORMAT_COMMAND_PATTERN
from ..config.generation.meshes import GLB_FORMATS, FORMAT_COMMANDS
from ..config.messages.inputs import (
    MESH_INPUT_EMPTY,
    MESH_PROMPT_LENGTH,
    MESH_FORMAT_COMMAND,
    MESH_IMAGE_REQUIRED,
)

if TYPE_CHECKING:
    from ..types import Json
    from ..types.settings import Settings
    from ..types.meshes import MeshRequest
    from ..types.models import MeshRow, ModelMatch

# A file format command in prompt text, such as "--fileformat obj", whose value must name GLB.
_FORMAT_COMMAND = re.compile(MESH_FORMAT_COMMAND_PATTERN, re.IGNORECASE)


def _build_text(request: MeshRequest, dialect: str) -> str:
    """Write the text item: the prompt as written, then the GLB format command unless the prompt already asks for GLB.

    A prompt that asks for another format is refused, since the node returns the file as GLB.
    """
    values = [value.lower() for value in _FORMAT_COMMAND.findall(request.prompt)]
    other = next((value for value in values if value != GLB_FORMATS[dialect]), None)
    if other is not None:
        message = MESH_FORMAT_COMMAND.format(value=other, command=FORMAT_COMMANDS[dialect])
        raise ByteplusError(ErrorCode.INVALID_INPUT, message)
    if values:
        return request.prompt
    return " ".join(word for word in (request.prompt, FORMAT_COMMANDS[dialect]) if word)


def validate_mesh_request(request: MeshRequest, settings: Settings) -> None:
    """Refuse, before the model row is read, a request no 3D model could take, and images over the upload limit.

    ModelArk reads image references itself, so only outputs and links are taken, and an output must not expire before
    the task starts.
    """
    if not request.prompt and not request.images and not request.references:
        raise ByteplusError(ErrorCode.INVALID_INPUT, MESH_INPUT_EMPTY)
    validate_upload_size([image.url for image in request.images], settings)
    validate_references(request.references, ("image",), can_read_assets=False, now=datetime.now(UTC))


def build_mesh_body(request: MeshRequest, match: ModelMatch[MeshRow]) -> dict[str, Json]:
    """Refuse, before anything is paid, what the model's row does not take, then build the body with Request Options.

    A model that reads no text, such as Hitem3D, takes its commands in the text item but still needs an image to work
    from. The text item comes first, then the images, then the image references. ModelArk cuts a longer text without
    an error, which could drop the format command the node adds, so a prompt that leaves it too little room is refused.
    """
    if not request.images and not request.references and "text" not in match.row.inputs:
        raise ByteplusError(ErrorCode.INVALID_INPUT, MESH_IMAGE_REQUIRED.format(model=match.model_id))
    limits = match.row.mesh
    text = _build_text(request, limits.dialect)
    if 0 < limits.max_prompt_characters < len(text):
        # The prompt is what the text holds beyond the added command and the space before it.
        maximum = limits.max_prompt_characters - (len(text) - len(request.prompt))
        raise ByteplusError(ErrorCode.INVALID_INPUT, MESH_PROMPT_LENGTH.format(model=match.model_id, maximum=maximum))
    content: list[Json] = [{"type": "text", "text": text}]
    content.extend({"type": "image_url", "image_url": {"url": image.url}} for image in request.images)
    content.extend({"type": "image_url", "image_url": {"url": reference.address}} for reference in request.references)
    return build_request_body({"model": match.model_id, "content": content}, request.options, "meshes", match.row)


__all__ = ["build_mesh_body", "validate_mesh_request"]
