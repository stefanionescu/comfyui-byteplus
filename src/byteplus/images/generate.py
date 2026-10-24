"""Send one request to ModelArk's image endpoint with a Seedream model and download the images it made."""

from __future__ import annotations

import re
from http import HTTPStatus
from typing import TYPE_CHECKING
from dataclasses import dataclass

from pydantic import ValidationError

from ..models import find_model, validate_value
from ..options import build_request_body
from ..uploads import validate_upload_size
from ..failures import build_failure
from ..transport import send_json, download_output
from ..references import validate_references
from ...state.errors import ErrorCode, BytePlusError
from ...state.images import ImageResult
from ...state.models import ImageRow
from ...state.replies import ImageReply
from ...config.byteplus import ENDPOINT_URLS
from ...config.patterns import IMAGE_SIZE_PATTERN
from ...state.references import OutputFile
from ...config.messages.run import REPLY_EMPTY, REPLY_UNREADABLE
from ...config.messages.inputs import (
    IMAGE_SIZE,
    PROMPT_EMPTY,
    IMAGE_COUNT_SINGLE,
    TRANSPARENT_FORMAT,
    TRANSPARENT_SOURCE,
)
from ...config.generation.images import RESPONSE_FORMAT

if TYPE_CHECKING:
    from ...state import Json
    from ...state.images import ImageRequest
    from ...state.models import ModelMatch, ImageLimits
    from ...state.settings import Settings, Configuration

_PIXEL_SIZE = re.compile(IMAGE_SIZE_PATTERN)


def _validate_background(request: ImageRequest, match: ModelMatch[ImageRow], background: str) -> None:
    """Refuse a transparent background the model or the request cannot make.

    ModelArk makes a transparent background only from exactly one input image that has an alpha channel, and writes
    it as PNG. A linked or output image is not checked for an alpha channel.
    """
    validate_value(match, 'background', background, match.row.image.backgrounds)
    has_one_source = len(request.images) + len(request.references) == 1
    if not has_one_source or (request.images and not request.images[0].has_alpha):
        raise BytePlusError(ErrorCode.INVALID_INPUT, TRANSPARENT_SOURCE)
    if request.output_format == 'jpeg':
        raise BytePlusError(ErrorCode.INVALID_INPUT, TRANSPARENT_FORMAT)


def _validate_image_request(request: ImageRequest, match: ModelMatch[ImageRow]) -> None:
    """Refuse what the model row does not take, before ModelArk bills anything.

    Seedream reads no assets, which only Seedance video takes. A size is one of the sizes of the model or any
    WIDTHxHEIGHT, whose pixels ModelArk checks itself.
    """
    limits = match.row.image
    validate_references(request.references, ('image',), can_read_assets=False)
    if request.size is not None and request.size not in limits.sizes and _PIXEL_SIZE.match(request.size) is None:
        message = IMAGE_SIZE.format(model=match.model_id, sizes=', '.join(limits.sizes))
        raise BytePlusError(ErrorCode.INVALID_INPUT, message)
    if request.max_images > 1 and not limits.has_sequential_image_generation:
        raise BytePlusError(ErrorCode.INVALID_INPUT, IMAGE_COUNT_SINGLE.format(model=match.model_id))
    if request.background is not None:
        _validate_background(request, match, request.background)
    if request.output_format is not None:
        validate_value(match, 'output_format', request.output_format, limits.output_formats)
    if request.optimize_prompt_mode is not None:
        validate_value(match, 'optimize_prompt_options', request.optimize_prompt_mode, limits.optimize_prompt_modes)


def _build_sequential_fields(max_images: int, limits: ImageLimits) -> dict[str, Json]:
    """Ask for up to max_images images in sequence, or turn sequential generation off for a single image.

    A model without sequential image generation gets no sequential field.
    """
    if max_images > 1:
        sequence: dict[str, Json] = {'max_images': max_images}
        return {'sequential_image_generation': 'auto', 'sequential_image_generation_options': sequence}
    return {'sequential_image_generation': 'disabled'} if limits.has_sequential_image_generation else {}


def _build_image_body(request: ImageRequest, match: ModelMatch[ImageRow]) -> dict[str, Json]:
    """Build the body of the checked request, with the options of Request Options.

    The body carries the size as typed, and an empty size sends none. ModelArk names the images Image 1, Image 2, and
    so on in the order of the image field: the local images first, then the references in chain order.
    """
    body: dict[str, Json] = {
        'model': match.model_id,
        'prompt': request.prompt,
        'response_format': RESPONSE_FORMAT,
        'watermark': request.has_watermark,
        **_build_sequential_fields(request.max_images, match.row.image),
    }
    if request.size is not None:
        body['size'] = request.size
    sources: list[Json] = [image.url for image in request.images]
    sources += [reference.address for reference in request.references]
    if sources:
        body['image'] = sources[0] if len(sources) == 1 else sources
    if request.background is not None:
        body['background'] = request.background
    if request.output_format is not None:
        body['output_format'] = request.output_format
    if request.optimize_prompt_mode is not None:
        body['optimize_prompt_options'] = {'mode': request.optimize_prompt_mode}
    return build_request_body(body, request.options, 'images', match.row)


def _list_addresses(reply: ImageReply) -> list[str]:
    """List the address of every image made, in reply order.

    The list leaves out an image that moderation refused. ModelArk does not bill it, and sequential image generation
    can make fewer images than asked anyway. When the reply holds no image, the first error stops the run with its own
    message, such as a moderation refusal.
    """
    addresses = [item.url for item in reply.images if item.url is not None]
    if addresses:
        return addresses
    errors = [reply.error, *(item.error for item in reply.images)]
    error = next((error for error in errors if error is not None), None)
    if error is None:
        raise BytePlusError(ErrorCode.TRANSPORT, REPLY_EMPTY)
    raise build_failure(HTTPStatus.OK, error.code, error.message)


def parse_image_reply(document: Json) -> ImageReply:
    """Read the reply of the image endpoint; ModelArk may have billed a reply that does not parse."""
    try:
        return ImageReply.model_validate(document)
    except ValidationError:
        raise BytePlusError(ErrorCode.UNCERTAIN, REPLY_UNREADABLE) from None


@dataclass(frozen=True, slots=True)
class ImageOperation:
    """One image request, sent once; ModelArk bills only the images it made.

    Attributes:
        request: The request to validate and send.

    """

    request: ImageRequest

    def validate(self, settings: Settings) -> None:
        """Refuse a blank prompt and more local image data than the maximum upload size."""
        if not self.request.prompt.strip():
            raise BytePlusError(ErrorCode.INVALID_INPUT, PROMPT_EMPTY)
        validate_upload_size((image.url for image in self.request.images), settings)

    async def send(self, configuration: Configuration) -> ImageResult:
        """Check the request against the model's row, send it, and download each image once, without the key."""
        request = self.request
        match = find_model(request.model_id, 'images', ImageRow)
        _validate_image_request(request, match)
        body = _build_image_body(request, match)
        reply = parse_image_reply(await send_json(ENDPOINT_URLS['images'], body, configuration))
        outputs = [
            OutputFile(await download_output(address, configuration.settings), address)
            for address in _list_addresses(reply)
        ]
        return ImageResult(tuple(outputs), created_at=reply.created)


__all__ = ['ImageOperation', 'parse_image_reply']
