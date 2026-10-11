"""Split one image into a base image and transparent layers with a Seedream model, and download them."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING
from ..failures import build_failure
from .generate import parse_image_reply
from ..options import build_request_body
from ...types.references import Reference
from ...config.byteplus import ENDPOINT_URLS
from ..operation import validate_upload_size
from ..references import validate_references
from ..models import find_model, validate_value
from ..transport import send_json, download_output
from ...config.messages.run import REPLY_UNREADABLE
from ...types.errors import ErrorCode, BytePlusError
from ...config.generation.images import RESPONSE_FORMAT
from ...types.images import Layer, LayerResult, EncodedImage

if TYPE_CHECKING:
    from ...types import Json
    from ...types.replies import ImageReply
    from ...types.images import LayerRequest
    from ...types.models import ImageRow, ModelMatch
    from ...types.settings import Settings, Configuration


def _validate_layer_request(request: LayerRequest, match: ModelMatch[ImageRow]) -> None:
    """Refuse, before anything is paid, a reference the model cannot read and an optimize prompt mode it does not take.

    Every layer model takes every size, and ModelArk checks the image's own size itself.
    """
    image = request.image
    if isinstance(image, Reference):
        validate_references((image,), ("image",), can_read_assets=False)
    if request.optimize_prompt_mode is not None:
        validate_value(
            match, "optimize prompt options", request.optimize_prompt_mode, match.row.image.optimize_prompt_modes
        )


def _build_layer_body(request: LayerRequest, match: ModelMatch[ImageRow]) -> dict[str, Json]:
    """Build the split's body, with the options of Request Options.

    Without a prompt ModelArk splits every main part. No output_format is sent: it would apply only to the base image,
    and layers are always PNG.
    """
    image = request.image
    body: dict[str, Json] = {
        "model": match.model_id,
        "image": image.url if isinstance(image, EncodedImage) else image.address,
        "layer_decomposition": True,
        "size": request.size,
        "response_format": RESPONSE_FORMAT,
        "watermark": request.has_watermark,
    }
    if request.prompt.strip():
        body["prompt"] = request.prompt
    if request.optimize_prompt_mode is not None:
        body["optimize_prompt_options"] = {"mode": request.optimize_prompt_mode}
    return build_request_body(body, request.options, "layers", match.row)


def _list_layers(reply: ImageReply) -> tuple[str, list[tuple[str, tuple[int, int, int, int]]]]:
    """List the base image's address, then each layer's address and box from bottom to top.

    A split succeeds or fails whole, so an error comes without images. A reply without one base image, or with an
    image that has no address or a layer that has no box, cannot be placed, though it may have been billed.
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


class LayerOperation:
    """One layer split, sent once; ModelArk bills every layer as an image."""

    def __init__(self, request: LayerRequest) -> None:
        """Keep the request to validate and send."""
        self.request = request

    def validate(self, settings: Settings) -> None:
        """Refuse a local image larger than the maximum upload size; a reference is read by ModelArk."""
        image = self.request.image
        if isinstance(image, EncodedImage):
            validate_upload_size((image.url,), settings)

    async def send(self, configuration: Configuration) -> LayerResult:
        """Check the request against the model's row, send it, and download the base and each layer once."""
        request = self.request
        match = find_model(request.model_id, "layers")
        _validate_layer_request(request, match)
        body = _build_layer_body(request, match)
        reply = parse_image_reply(await send_json(ENDPOINT_URLS["images"], body, configuration))
        base, boxes = _list_layers(reply)
        settings = configuration.settings
        base_content = await download_output(base, settings)
        layers = [Layer(await download_output(address, settings), box) for address, box in boxes]
        return LayerResult(base_content, tuple(layers))


__all__ = ["LayerOperation"]
