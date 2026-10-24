"""Split one image into a base image and transparent layers with a Seedream model, and download them."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING
from dataclasses import dataclass

from ..models import find_model, validate_value
from ..options import build_request_body
from ..uploads import validate_upload_size
from .generate import parse_image_reply
from ..failures import build_failure
from ..transport import send_json, download_output
from ..references import validate_references
from ...state.errors import ErrorCode, BytePlusError
from ...state.images import Layer, LayerResult, EncodedImage
from ...state.models import ImageRow
from ...config.byteplus import ENDPOINT_URLS
from ...state.references import Reference
from ...config.messages.run import REPLY_UNREADABLE
from ...config.generation.images import RESPONSE_FORMAT

if TYPE_CHECKING:
    from ...state import Json
    from ...state.images import LayerRequest
    from ...state.models import ModelMatch
    from ...state.replies import ImageReply
    from ...state.settings import Settings, Configuration


def _validate_layer_request(request: LayerRequest, match: ModelMatch[ImageRow]) -> None:
    """Refuse an unreadable reference and an optimize prompt mode the model lacks, before ModelArk bills anything.

    Every layer model takes every size, and ModelArk checks the size of the image itself.
    """
    image = request.image
    if isinstance(image, Reference):
        validate_references((image,), ('image',), can_read_assets=False)
    if request.optimize_prompt_mode is not None:
        validate_value(
            match, 'optimize_prompt_options', request.optimize_prompt_mode, match.row.image.optimize_prompt_modes
        )


def _build_layer_body(request: LayerRequest, match: ModelMatch[ImageRow]) -> dict[str, Json]:
    """Build the body of the split, with the options of Request Options.

    Without a prompt ModelArk splits every main part. The body sends no output_format, because that field applies only
    to the base image and layers are always PNG.
    """
    image = request.image
    body: dict[str, Json] = {
        'model': match.model_id,
        'image': image.url if isinstance(image, EncodedImage) else image.address,
        'layer_decomposition': True,
        'size': request.size,
        'response_format': RESPONSE_FORMAT,
        'watermark': request.has_watermark,
    }
    if request.prompt.strip():
        body['prompt'] = request.prompt
    if request.optimize_prompt_mode is not None:
        body['optimize_prompt_options'] = {'mode': request.optimize_prompt_mode}
    return build_request_body(body, request.options, 'layers', match.row)


def _list_layers(reply: ImageReply) -> tuple[str, list[tuple[str, tuple[int, int, int, int]]]]:
    """List the address of the base image, then the address and box of each layer from bottom to top.

    A split succeeds or fails whole, so an error comes without images. This function cannot place the layers of a
    reply that lacks one base image, an image address, or a layer box, though ModelArk may have billed that reply.
    """
    if reply.error is not None and not reply.images:
        raise build_failure(HTTPStatus.OK, reply.error.code, reply.error.message)
    bases = [item.url for item in reply.images if item.z_index == 0]
    items = sorted((item for item in reply.images if item.z_index > 0), key=lambda item: item.z_index)
    layers = [
        (item.url, item.bounding_box.absolute)
        for item in items
        if item.url is not None and item.bounding_box is not None
    ]
    if len(bases) != 1 or bases[0] is None or len(layers) != len(items):
        raise BytePlusError(ErrorCode.UNCERTAIN, REPLY_UNREADABLE)
    return bases[0], layers


@dataclass(frozen=True, slots=True)
class LayerOperation:
    """One layer split, sent once; ModelArk bills every layer as an image.

    Attributes:
        request: The request to validate and send.

    """

    request: LayerRequest

    def validate(self, settings: Settings) -> None:
        """Refuse a local image larger than the maximum upload size; ModelArk reads a reference itself."""
        image = self.request.image
        if isinstance(image, EncodedImage):
            validate_upload_size((image.url,), settings)

    async def send(self, configuration: Configuration) -> LayerResult:
        """Check the request against the model's row, send it, and download the base and each layer once."""
        request = self.request
        match = find_model(request.model_id, 'layers', ImageRow)
        _validate_layer_request(request, match)
        body = _build_layer_body(request, match)
        reply = parse_image_reply(await send_json(ENDPOINT_URLS['images'], body, configuration))
        base, boxes = _list_layers(reply)
        settings = configuration.settings
        base_content = await download_output(base, settings)
        layers = [Layer(await download_output(address, settings), box) for address, box in boxes]
        return LayerResult(base_content, tuple(layers))


__all__ = ['LayerOperation']
