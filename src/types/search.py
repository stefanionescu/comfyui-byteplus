"""Embedding requests and results; items are numbered texts first, then images, then videos, in input order."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .options import Options
    from .images import EncodedImage


@dataclass(frozen=True, slots=True)
class EmbeddingRequest:
    """One Search: Embed run with its media already encoded; each item is sent in its own request.

    Attributes:
        model_id: The model ID sent to ModelArk.
        texts: Text items: every non-blank line, trimmed.
        images: Image items, in list order and then batch order.
        video_urls: MP4 data URLs of video items.
        dimensions: The vector length, or None for the model's default.
        instructions: The instructions sent as written with every item; None sends none.
        options: The service tier and extra fields from Request Options.

    """

    model_id: str
    texts: tuple[str, ...]
    images: tuple[EncodedImage, ...]
    video_urls: tuple[str, ...]
    dimensions: int | None
    instructions: str | None
    options: Options | None


@dataclass(frozen=True, slots=True)
class EmbeddingResult:
    """One vector per item, and how similar each item is to the first.

    Attributes:
        vectors: The vectors in item order.
        similarities: The cosine similarity of each vector with the first.

    """

    vectors: tuple[tuple[float, ...], ...]
    similarities: tuple[float, ...]


__all__ = ["EmbeddingRequest", "EmbeddingResult"]
