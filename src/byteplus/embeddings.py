"""Send one embedding request per item to ModelArk and compare each item's vector with the first.

ModelArk embeds everything in one request as a single vector, so each text, image, and video goes in its own request.
"""

from __future__ import annotations

import math
from .models import find_model
from .transport import send_json
from typing import TYPE_CHECKING
from pydantic import ValidationError
from .options import build_request_body
from ..types.replies import EmbeddingReply
from ..types.search import EmbeddingResult
from ..config.byteplus import ENDPOINT_URLS
from ..config.units import BYTES_PER_MEGABYTE
from ..config.messages.run import REPLY_UNREADABLE
from ..types.errors import ErrorCode, ByteplusError
from .operation import validate_upload_size, measure_encoded_bytes
from ..config.generation.search import IMAGE_SHAPE, MAX_TEXT_BYTES, MAX_VIDEO_BYTES
from ..config.messages.inputs import (
    SEARCH_TEXT_SIZE,
    SEARCH_DIMENSIONS,
    SEARCH_VIDEO_SIZE,
    SEARCH_IMAGE_SHAPE,
    SEARCH_ITEMS_EMPTY,
    SEARCH_ITEM_STOPPED,
)

if TYPE_CHECKING:
    from ..types import Json
    from collections.abc import Sequence
    from ..types.search import EmbeddingRequest
    from ..types.models import ModelMatch, EmbeddingRow
    from ..types.settings import Settings, Configuration


def _validate_items(request: EmbeddingRequest) -> None:
    """Refuse a text, an image, or a video ModelArk does not embed; each is numbered within its kind.

    ModelArk's video limit counts the file, not its base64 text.
    """
    for number, text in enumerate(request.texts, 1):
        if len(text.encode()) > MAX_TEXT_BYTES:
            raise ByteplusError(ErrorCode.INVALID_INPUT, SEARCH_TEXT_SIZE.format(number=number))
    for number, image in enumerate(request.images, 1):
        short_side, long_side = sorted((image.width, image.height))
        if short_side < IMAGE_SHAPE["MIN_SIDE"] or long_side > IMAGE_SHAPE["MAX_ASPECT"] * short_side:
            message = SEARCH_IMAGE_SHAPE.format(number=number, width=image.width, height=image.height)
            raise ByteplusError(ErrorCode.INVALID_INPUT, message)
    for number, url in enumerate(request.video_urls, 1):
        size = measure_encoded_bytes(url)
        if size > MAX_VIDEO_BYTES:
            shown = math.ceil(size * 10 / BYTES_PER_MEGABYTE) / 10
            raise ByteplusError(ErrorCode.INVALID_INPUT, SEARCH_VIDEO_SIZE.format(number=number, size=shown))


def _validate_row(request: EmbeddingRequest, match: ModelMatch[EmbeddingRow]) -> None:
    """Refuse a vector length the model does not make."""
    choices = match.row.embedding.dimensions
    if request.dimensions is not None and request.dimensions not in choices:
        listed = " or ".join(str(choice) for choice in choices)
        raise ByteplusError(ErrorCode.INVALID_INPUT, SEARCH_DIMENSIONS.format(model=match.model_id, choices=listed))


def _list_items(request: EmbeddingRequest) -> tuple[Json, ...]:
    """List each item's content part, in item order: the texts, then the images, then the videos."""
    texts: list[Json] = [{"type": "text", "text": text} for text in request.texts]
    images: list[Json] = [{"type": "image_url", "image_url": {"url": image.url}} for image in request.images]
    videos: list[Json] = [{"type": "video_url", "video_url": {"url": url}} for url in request.video_urls]
    return (*texts, *images, *videos)


def _build_bodies(request: EmbeddingRequest, row: EmbeddingRow) -> list[dict[str, Json]]:
    """Build one body per item, in item order, each with the instructions as written and the options.

    Every body is built before the first is sent, so options the request cannot take are refused before anything is
    paid.
    """
    bodies: list[dict[str, Json]] = []
    for part in _list_items(request):
        body: dict[str, Json] = {"model": request.model_id, "input": [part]}
        if request.dimensions is not None:
            body["dimensions"] = request.dimensions
        if request.instructions is not None:
            body["instructions"] = request.instructions
        bodies.append(build_request_body(body, request.options, "embeddings", row))
    return bodies


def _parse_vector(document: Json, vectors: Sequence[tuple[float, ...]]) -> tuple[float, ...]:
    """Read one item's vector, which must be as long as the vectors read before it.

    The request was paid, so a reply that cannot be read leaves its outcome uncertain.
    """
    try:
        vector = EmbeddingReply.model_validate(document).vector.embedding
    except ValidationError:
        raise ByteplusError(ErrorCode.UNCERTAIN, REPLY_UNREADABLE) from None
    if not vector or (vectors and len(vector) != len(vectors[0])):
        raise ByteplusError(ErrorCode.UNCERTAIN, REPLY_UNREADABLE)
    return vector


def _build_similarities(vectors: Sequence[tuple[float, ...]]) -> tuple[float, ...]:
    """Compare each vector with the first by cosine similarity, as ModelArk's guide does; a zero-length vector is 0.

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


class EmbeddingOperation:
    """One Search: Embed run: one embedding request per item, sent one after another, each once."""

    def __init__(self, request: EmbeddingRequest) -> None:
        """Keep the request to validate and send."""
        self.request = request

    def validate(self, settings: Settings) -> None:
        """Refuse no items, an item ModelArk does not embed, and media above the maximum upload size.

        Every item is checked before the first request, so a refusal never leaves earlier items billed for nothing.
        The maximum upload size bounds the media of the whole run.
        """
        request = self.request
        if not (request.texts or request.images or request.video_urls):
            raise ByteplusError(ErrorCode.INVALID_INPUT, SEARCH_ITEMS_EMPTY)
        _validate_items(request)
        validate_upload_size((*(image.url for image in request.images), *request.video_urls), settings)

    async def send(self, configuration: Configuration) -> EmbeddingResult:
        """Check the request against the model's row, send the items in order, and compare each with the first.

        One request is in flight at a time. A failure stops the run and nothing is sent again: the items before it
        were sent and may be billed, so the message names the item that failed. A cancel passes through.
        """
        request = self.request
        match = find_model(request.model_id, "embeddings")
        _validate_row(request, match)
        bodies = _build_bodies(request, match.row)
        vectors: list[tuple[float, ...]] = []
        for number, body in enumerate(bodies, 1):
            try:
                document = await send_json(ENDPOINT_URLS["embeddings"], body, configuration)
                vectors.append(_parse_vector(document, vectors))
            except ByteplusError as error:
                if len(bodies) == 1:
                    raise
                message = SEARCH_ITEM_STOPPED.format(number=number, count=len(bodies), message=str(error))
                raise ByteplusError(error.code, message) from None
        return EmbeddingResult(tuple(vectors), _build_similarities(vectors))


__all__ = ["EmbeddingOperation"]
