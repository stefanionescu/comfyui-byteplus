"""Send one request to ModelArk's image endpoint with a Seedream model and download the images it made."""

from __future__ import annotations

import re
from http import HTTPStatus
from typing import TYPE_CHECKING
from datetime import UTC, datetime
from ..failures import build_failure
from pydantic import ValidationError
from ...types.replies import ImageReply
from ..options import build_request_body
from ...config.byteplus import ENDPOINT_URLS
from ..operation import validate_upload_size
from ..references import validate_references
from ..models import find_model, validate_value
from ...config.patterns import IMAGE_SIZE_PATTERN
from ..transport import send_json, download_output
from ...types.errors import ErrorCode, ByteplusError
from ...types.images import ImageOutput, ImageResult
from ...config.generation.images import RESPONSE_FORMAT
from ...config.messages.run import REPLY_EMPTY, REPLY_UNREADABLE
from ...config.messages.inputs import (
    IMAGE_SIZE,
    PROMPT_EMPTY,
    IMAGE_COUNT_SINGLE,
    TRANSPARENT_FORMAT,
    TRANSPARENT_SOURCE,
)

if TYPE_CHECKING:
    from ...types import Json
    from ...types.images import ImageRequest
    from ...types.settings import Settings, Configuration
    from ...types.models import ImageRow, ModelMatch, ImageLimits

_PIXEL_SIZE = re.compile(IMAGE_SIZE_PATTERN)


def _validate_background(request: ImageRequest, match: ModelMatch[ImageRow], background: str) -> None:
    """Refuse a transparent background the model or the request cannot make.

    ModelArk keeps the transparency of exactly one reference image, which must have an alpha channel, and writes it
    as PNG. A linked or output image is not measured.
    """
    validate_value(match, "background", background, match.row.image.backgrounds)
    has_one_source = len(request.images) + len(request.references) == 1
    if not has_one_source or (request.images and not request.images[0].has_alpha):
        raise ByteplusError(ErrorCode.INVALID_INPUT, TRANSPARENT_SOURCE)
    if request.output_format == "jpeg":
        raise ByteplusError(ErrorCode.INVALID_INPUT, TRANSPARENT_FORMAT)


def _validate_image_request(request: ImageRequest, match: ModelMatch[ImageRow]) -> None:
    """Refuse, before anything is paid, what the model's row does not take; the first refusal stops the check.

    Seedream reads no assets, which only Seedance video takes. A size is one of the model's tiers or any WIDTHxHEIGHT,
    whose pixels ModelArk checks itself.
    """
    limits = match.row.image
    validate_references(request.references, ("image",), can_read_assets=False, now=datetime.now(UTC))
    if request.size is not None and request.size not in limits.tiers and _PIXEL_SIZE.match(request.size) is None:
        message = IMAGE_SIZE.format(model=match.model_id, tiers=", ".join(limits.tiers))
        raise ByteplusError(ErrorCode.INVALID_INPUT, message)
    if request.max_images > 1 and not limits.has_series:
        raise ByteplusError(ErrorCode.INVALID_INPUT, IMAGE_COUNT_SINGLE.format(model=match.model_id))
    if request.background is not None:
        _validate_background(request, match, request.background)
    if request.output_format is not None:
        validate_value(match, "output format", request.output_format, limits.output_formats)
    if request.prompt_mode is not None:
        validate_value(match, "optimize prompt options", request.prompt_mode, limits.prompt_modes)


def _build_series_fields(max_images: int, limits: ImageLimits) -> dict[str, Json]:
    """Ask a series model for up to max_images images, or turn its series off for one; other models take no field."""
    if max_images > 1:
        series: dict[str, Json] = {"max_images": max_images}
        return {"sequential_image_generation": "auto", "sequential_image_generation_options": series}
    return {"sequential_image_generation": "disabled"} if limits.has_series else {}


def _build_image_body(request: ImageRequest, match: ModelMatch[ImageRow]) -> dict[str, Json]:
    """Build the checked request's body, with the options of Request Options.

    The size is sent as typed, and an empty size sends none. ModelArk names the images Image 1, Image 2, and so on
    in the order of image: the local images first, then the references in chain order.
    """
    body: dict[str, Json] = {
        "model": match.model_id,
        "prompt": request.prompt,
        "response_format": RESPONSE_FORMAT,
        "watermark": request.has_watermark,
        **_build_series_fields(request.max_images, match.row.image),
    }
    if request.size is not None:
        body["size"] = request.size
    sources: list[Json] = [image.url for image in request.images]
    sources += [reference.address for reference in request.references]
    if sources:
        body["image"] = sources[0] if len(sources) == 1 else sources
    if request.background is not None:
        body["background"] = request.background
    if request.output_format is not None:
        body["output_format"] = request.output_format
    if request.prompt_mode is not None:
        body["optimize_prompt_options"] = {"mode": request.prompt_mode}
    return build_request_body(body, request.options, "images", match.row)


def _list_addresses(reply: ImageReply) -> list[str]:
    """List the address of every image made, in reply order.

    An image moderation refused is left out; it is not billed, and a series may make fewer images than asked in any
    case. When none was made, the first error stops the run with its own message, such as a moderation refusal.
    """
    addresses = [item.url for item in reply.images if item.url is not None]
    if addresses:
        return addresses
    errors = [reply.error, *(item.error for item in reply.images)]
    error = next((error for error in errors if error is not None), None)
    if error is None:
        raise ByteplusError(ErrorCode.TRANSPORT, REPLY_EMPTY)
    raise build_failure(HTTPStatus.OK, error.code, error.message)


def parse_image_reply(document: Json) -> ImageReply:
    """Read the image endpoint's reply; one that does not parse may still have been billed."""
    try:
        return ImageReply.model_validate(document)
    except ValidationError:
        raise ByteplusError(ErrorCode.UNCERTAIN, REPLY_UNREADABLE) from None


class ImageOperation:
    """One image request, sent once; ModelArk bills only the images it made."""

    def __init__(self, request: ImageRequest) -> None:
        """Keep the request to validate and send."""
        self.request = request

    def validate(self, settings: Settings) -> None:
        """Refuse a blank prompt and more local image data than the maximum upload size."""
        if not self.request.prompt.strip():
            raise ByteplusError(ErrorCode.INVALID_INPUT, PROMPT_EMPTY)
        validate_upload_size((image.url for image in self.request.images), settings)

    async def send(self, configuration: Configuration) -> ImageResult:
        """Check the request against the model's row, send it, and download each image once, without the key."""
        request = self.request
        match = find_model(request.model_id, "images")
        _validate_image_request(request, match)
        body = _build_image_body(request, match)
        reply = parse_image_reply(await send_json(ENDPOINT_URLS["images"], body, configuration))
        outputs = [
            ImageOutput(await download_output(address, configuration.settings), address)
            for address in _list_addresses(reply)
        ]
        return ImageResult(tuple(outputs), created_at=reply.created)


__all__ = ["ImageOperation", "parse_image_reply"]
