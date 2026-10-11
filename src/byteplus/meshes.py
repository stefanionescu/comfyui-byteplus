"""Check a 3D request against what every 3D model and its own row take, and build the task body.

Hyper3D and Hitem3D read their settings as --name value commands after the prompt, so the node writes the commands
itself and refuses a prompt that already holds one.
"""

from __future__ import annotations

import re
import math
from typing import TYPE_CHECKING
from datetime import UTC, datetime
from .options import build_request_body
from .references import validate_references
from ..config.units import BYTES_PER_MEGABYTE
from .models import validate_range, validate_value
from ..types.errors import ErrorCode, ByteplusError
from ..config.generation.inputs import MODEL_DEFAULT
from .operation import validate_upload_size, measure_encoded_bytes
from ..config.messages.inputs import (
    MESH_VIEWS,
    MESH_IMAGE_SIZE,
    MESH_IMAGE_COUNT,
    MESH_INPUT_EMPTY,
    MESH_VIEWS_COUNT,
    MESH_IMAGE_PIXELS,
    MESH_PROMPT_LENGTH,
    MESH_PROMPT_COMMAND,
    MESH_PROMPT_UNSUPPORTED,
    MESH_IMAGES_ADDRESS_ONLY,
)
from ..config.generation.meshes import (
    POSES,
    VIEWS,
    COMMAND_NAMES,
    FACE_COMMANDS,
    POSE_COMMANDS,
    VIEW_COMMANDS,
    FORMAT_COMMANDS,
    TEXTURE_COMMANDS,
    IMAGE_BYTES_BELOW,
    TOPOLOGY_COMMANDS,
    IMAGE_PIXELS_BELOW,
    PRECISION_COMMANDS,
)

if TYPE_CHECKING:
    from ..types import Json
    from ..types.settings import Settings
    from ..types.meshes import MeshRequest
    from ..types.models import MeshRow, ModelMatch

# A 3D command in prompt text, such as "--material None", which would conflict with the commands the node writes.
_MESH_COMMAND = re.compile(rf"--({'|'.join(re.escape(name) for name in COMMAND_NAMES)})\b", re.IGNORECASE)


def _validate_images(request: MeshRequest) -> None:
    """Refuse a local image with as many pixels as 4096 by 4096, or as large as 30 MB as PNG; each is numbered.

    ModelArk's size limit counts the file, not its base64 text.
    """
    for number, image in enumerate(request.images, 1):
        if image.width * image.height >= IMAGE_PIXELS_BELOW:
            message = MESH_IMAGE_PIXELS.format(number=number, width=image.width, height=image.height)
            raise ByteplusError(ErrorCode.INVALID_INPUT, message)
        size = measure_encoded_bytes(image.url)
        if size >= IMAGE_BYTES_BELOW:
            shown = math.ceil(size * 10 / BYTES_PER_MEGABYTE) / 10
            raise ByteplusError(ErrorCode.INVALID_INPUT, MESH_IMAGE_SIZE.format(number=number, size=shown))


def _validate_sources(request: MeshRequest, match: ModelMatch[MeshRow]) -> None:
    """Refuse local images to a model that reads only addresses, a prompt it does not read, and too many images.

    Images and image references count together, since each becomes one image item.
    """
    limits = match.row.mesh
    if request.images and not limits.has_inline_images:
        raise ByteplusError(ErrorCode.INVALID_INPUT, MESH_IMAGES_ADDRESS_ONLY.format(model=match.model_id))
    if request.prompt and limits.max_prompt_characters == 0:
        raise ByteplusError(ErrorCode.INVALID_INPUT, MESH_PROMPT_UNSUPPORTED.format(model=match.model_id))
    count = len(request.images) + len(request.references)
    if count > limits.max_images:
        message = MESH_IMAGE_COUNT.format(model=match.model_id, maximum=limits.max_images, count=count)
        raise ByteplusError(ErrorCode.INVALID_INPUT, message)


def _validate_settings(request: MeshRequest, match: ModelMatch[MeshRow]) -> None:
    """Refuse a texture, mesh, precision, pose, views, or face count the model does not take.

    The faces allowed depend on the mesh; the row's model default range is the one of the model's default mesh.
    """
    limits = match.row.mesh
    # A model that takes a pose takes the one pose choice.
    chosen = (
        ("texture", request.texture, limits.textures),
        ("mesh", request.topology, limits.topologies),
        ("precision", request.precision, limits.precisions),
        ("pose", request.pose, POSES[1:] if limits.has_pose else ()),
    )
    for label, value, values in chosen:
        if value is not None:
            validate_value(match, label, value, values)
    for view in request.views:
        validate_value(match, "views", view, VIEWS if limits.has_views else ())
    count = len(request.images) + len(request.references)
    if request.views and len(request.views) != count:
        raise ByteplusError(ErrorCode.INVALID_INPUT, MESH_VIEWS_COUNT.format(views=len(request.views), count=count))
    validate_range(match, "faces", request.faces, limits.face_ranges[request.topology or MODEL_DEFAULT], (0,))


def _build_text(request: MeshRequest, dialect: str) -> str:
    """Write the text item: the prompt, then a command for each setting that is set, then the GLB format, always.

    The commands follow the order of Hitem3D's own example. The view bits hold one character per side of VIEWS, 1
    where an image shows it, so front and left become 1010.
    """
    words = [request.prompt] if request.prompt else []
    tables = (
        (request.precision, PRECISION_COMMANDS),
        (request.texture, TEXTURE_COMMANDS),
        (request.topology, TOPOLOGY_COMMANDS),
    )
    words.extend(commands[dialect][value] for value, commands in tables if value is not None)
    if request.faces > 0:
        words.append(FACE_COMMANDS[dialect].format(faces=request.faces))
    if request.pose is not None:
        words.append(POSE_COMMANDS[dialect][request.pose])
    if request.views:
        bits = "".join("1" if view in request.views else "0" for view in VIEWS)
        words.append(VIEW_COMMANDS[dialect].format(bits=bits))
    words.append(FORMAT_COMMANDS[dialect])
    return " ".join(words)


def validate_mesh_request(request: MeshRequest, settings: Settings) -> None:
    """Refuse, before the model row is read, a request no 3D model could take, and images over the upload limit.

    Views name each side once, in the order of VIEWS, which is the order of Hitem3D's view bits. ModelArk reads image
    references itself, so only outputs and links are taken, and an output must not expire before the task starts.
    """
    if not request.prompt and not request.images and not request.references:
        raise ByteplusError(ErrorCode.INVALID_INPUT, MESH_INPUT_EMPTY)
    command = _MESH_COMMAND.search(request.prompt)
    if command is not None:
        raise ByteplusError(ErrorCode.INVALID_INPUT, MESH_PROMPT_COMMAND.format(name=command.group(1)))
    _validate_images(request)
    if list(request.views) != [view for view in VIEWS if view in request.views]:
        raise ByteplusError(ErrorCode.INVALID_INPUT, MESH_VIEWS)
    validate_upload_size([image.url for image in request.images], settings)
    validate_references(request.references, frozenset({"image"}), can_read_assets=False, now=datetime.now(UTC))


def build_mesh_body(request: MeshRequest, match: ModelMatch[MeshRow]) -> dict[str, Json]:
    """Refuse, before anything is paid, what the model's row does not take, then build the body with Request Options.

    The text item comes first, then the images, then the image references. ModelArk cuts a longer text without an
    error, which could drop the node's own commands, so a prompt that leaves the commands too little room is refused.
    """
    _validate_sources(request, match)
    _validate_settings(request, match)
    limits = match.row.mesh
    text = _build_text(request, limits.dialect)
    if 0 < limits.max_prompt_characters < len(text):
        # The prompt is what the text holds beyond the commands and the space before them.
        maximum = limits.max_prompt_characters - (len(text) - len(request.prompt))
        raise ByteplusError(ErrorCode.INVALID_INPUT, MESH_PROMPT_LENGTH.format(model=match.model_id, maximum=maximum))
    content: list[Json] = [{"type": "text", "text": text}]
    content.extend({"type": "image_url", "image_url": {"url": image.url}} for image in request.images)
    content.extend({"type": "image_url", "image_url": {"url": reference.address}} for reference in request.references)
    return build_request_body({"model": match.model_id, "content": content}, request.options, "meshes", match.row)


__all__ = ["build_mesh_body", "validate_mesh_request"]
