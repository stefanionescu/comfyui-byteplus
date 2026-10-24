"""Send one embedding request per item to ModelArk and compare each item's vector with the first.

ModelArk embeds everything in one request as a single vector, so each text, image, and video goes in its own request.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING
from dataclasses import dataclass

from pydantic import ValidationError

from .models import find_model
from .options import build_request_body
from .uploads import validate_upload_size
from .transport import send_json
from ..config.units import BYTES_PER_MEGABYTE
from ..state.errors import ErrorCode, BytePlusError
from ..state.models import EmbeddingRow
from ..state.search import EmbeddingResult
from ..state.replies import EmbeddingReply
from ..config.byteplus import ENDPOINT_URLS
from ..config.messages.run import REPLY_UNREADABLE
from ..config.messages.inputs import (
    SEARCH_TEXT_SIZE,
    SEARCH_DIMENSIONS,
    SEARCH_VIDEO_SIZE,
    SEARCH_IMAGE_SHAPE,
    SEARCH_ITEMS_EMPTY,
    SEARCH_ITEM_STOPPED,
)
from ..config.generation.search import IMAGE_SHAPE, MAX_TEXT_BYTES, MAX_VIDEO_BYTES

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ..state import Json
    from ..state.models import ModelMatch
    from ..state.search import EmbeddingRequest
    from ..state.settings import Settings, Configuration


def _validate_items(request: EmbeddingRequest) -> None:
    """Refuse a text, an image, or a video that ModelArk does not embed; the message numbers it within its kind.

    The video limit of ModelArk counts the file, not its base64 text.
    """
    for number, text in enumerate(request.texts, 1):
        if len(text.encode()) > MAX_TEXT_BYTES:
            raise BytePlusError(ErrorCode.INVALID_INPUT, SEARCH_TEXT_SIZE.format(number=number))
    for number, image in enumerate(request.images, 1):
        short_side, long_side = sorted((image.width, image.height))
        if short_side < IMAGE_SHAPE['MIN_SIDE'] or long_side > IMAGE_SHAPE['MAX_ASPECT'] * short_side:
            message = SEARCH_IMAGE_SHAPE.format(number=number, width=image.width, height=image.height)
            raise BytePlusError(ErrorCode.INVALID_INPUT, message)
    for number, url in enumerate(request.video_urls, 1):
        # The file's size, measured from the data URL's base64 text without decoding it.
        encoded = url.partition(',')[2]
        size = len(encoded) * 3 // 4 - (len(encoded) - len(encoded.rstrip('=')))
        if size > MAX_VIDEO_BYTES:
            shown = math.ceil(size * 10 / BYTES_PER_MEGABYTE) / 10
            raise BytePlusError(ErrorCode.INVALID_INPUT, SEARCH_VIDEO_SIZE.format(number=number, size=shown))


def _validate_row(request: EmbeddingRequest, match: ModelMatch[EmbeddingRow]) -> None:
    """Refuse a vector length the model does not make."""
    choices = match.row.embedding.dimensions
    if request.dimensions is not None and request.dimensions not in choices:
        listed = ' or '.join(str(choice) for choice in choices)
        raise BytePlusError(ErrorCode.INVALID_INPUT, SEARCH_DIMENSIONS.format(model=match.model_id, choices=listed))


def _list_items(request: EmbeddingRequest) -> tuple[Json, ...]:
    """List each item's content part, in item order: the texts, then the images, then the videos."""
    texts: list[Json] = [{'type': 'text', 'text': text} for text in request.texts]
    images: list[Json] = [{'type': 'image_url', 'image_url': {'url': image.url}} for image in request.images]
    videos: list[Json] = [{'type': 'video_url', 'video_url': {'url': url}} for url in request.video_urls]
    return (*texts, *images, *videos)


def _build_bodies(request: EmbeddingRequest, row: EmbeddingRow) -> list[dict[str, Json]]:
    """Build one body per item, in item order, each with the instructions as written and the options.

    It builds every body before the first request goes out, so it refuses an option that the request cannot take
    before ModelArk bills anything.
    """
    bodies: list[dict[str, Json]] = []
    for part in _list_items(request):
        body: dict[str, Json] = {'model': request.model_id, 'input': [part]}
        if request.dimensions is not None:
            body['dimensions'] = request.dimensions
        if request.instructions is not None:
            body['instructions'] = request.instructions
        bodies.append(build_request_body(body, request.options, 'embeddings', row))
    return bodies


def _parse_vector(document: Json, vectors: Sequence[tuple[float, ...]]) -> tuple[float, ...]:
    """Read the vector of one item, which must be as long as the vectors read before it.

    ModelArk has billed the request, so an unreadable reply leaves its outcome uncertain.
    """
    try:
        vector = EmbeddingReply.model_validate(document).vector.embedding
    except ValidationError:
        raise BytePlusError(ErrorCode.UNCERTAIN, REPLY_UNREADABLE) from None
    if not vector or (vectors and len(vector) != len(vectors[0])):
        raise BytePlusError(ErrorCode.UNCERTAIN, REPLY_UNREADABLE)
    return vector


def _build_similarities(vectors: Sequence[tuple[float, ...]]) -> tuple[float, ...]:
    """Compare each vector with the first by cosine similarity, as ModelArk's guide does; an all-zero vector scores 0.

    math.fsum adds the products without rounding error building up over thousands of values.
    """
    first = vectors[0]
    first_length = math.sqrt(math.fsum(value * value for value in first))
    similarities: list[float] = []
    for vector in vectors:
        length = first_length * math.sqrt(math.fsum(value * value for value in vector))
        dot = math.fsum(left * right for left, right in zip(first, vector, strict=True))
        similarities.append(dot / length if length else 0.0)
    return tuple(similarities)


@dataclass(frozen=True, slots=True)
class EmbeddingOperation:
    """One Search: Embed run, which sends one embedding request per item, one after another, each once.

    Attributes:
        request: The request to validate and send.

    """

    request: EmbeddingRequest

    def validate(self, settings: Settings) -> None:
        """Refuse no items, an item ModelArk does not embed, and media above the maximum upload size.

        This method checks every item before the first request, so a refusal never leaves earlier items billed for
        nothing.
        The maximum upload size bounds the media of the whole run.
        """
        request = self.request
        if not (request.texts or request.images or request.video_urls):
            raise BytePlusError(ErrorCode.INVALID_INPUT, SEARCH_ITEMS_EMPTY)
        _validate_items(request)
        validate_upload_size((*(image.url for image in request.images), *request.video_urls), settings)

    async def send(self, configuration: Configuration) -> EmbeddingResult:
        """Check the request against the model row, send the items in order, and compare each with the first.

        One request is in flight at a time. A failure stops the run, and the method sends nothing again. ModelArk may
        bill the items sent before the failure, so the message names the item that failed. A cancel passes through.
        """
        request = self.request
        match = find_model(request.model_id, 'embeddings', EmbeddingRow)
        _validate_row(request, match)
        bodies = _build_bodies(request, match.row)
        vectors: list[tuple[float, ...]] = []
        for number, body in enumerate(bodies, 1):
            try:
                document = await send_json(ENDPOINT_URLS['embeddings'], body, configuration)
                vectors.append(_parse_vector(document, vectors))
            except BytePlusError as error:
                if len(bodies) == 1:
                    raise
                message = SEARCH_ITEM_STOPPED.format(number=number, count=len(bodies), message=str(error))
                raise BytePlusError(error.code, message) from None
        return EmbeddingResult(tuple(vectors), _build_similarities(vectors))


__all__ = ['EmbeddingOperation']
