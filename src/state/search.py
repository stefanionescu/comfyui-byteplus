"""Embedding requests and results; item numbers count texts first, then images, then videos, in input order."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

from .options import ModelRequest

if TYPE_CHECKING:
    from .images import EncodedImage


@dataclass(frozen=True, slots=True, kw_only=True)
class EmbeddingRequest(ModelRequest):
    """One Search: Embed run with its media already encoded; each item goes in its own request.

    Attributes:
        texts: Text items: every non-blank line, trimmed.
        images: Image items, in list order, then batch order.
        video_urls: MP4 data URLs of video items.
        dimensions: The vector length, or None for the model's default.
        instructions: The instructions sent as written with every item; None sends none.

    """

    texts: tuple[str, ...]
    images: tuple[EncodedImage, ...]
    video_urls: tuple[str, ...]
    dimensions: int | None
    instructions: str | None


@dataclass(frozen=True, slots=True)
class EmbeddingResult:
    """One vector per item, and how similar each item is to the first.

    Attributes:
        vectors: The vectors in item order.
        similarities: The cosine similarity of each vector with the first.

    """

    vectors: tuple[tuple[float, ...], ...]
    similarities: tuple[float, ...]


__all__ = ['EmbeddingRequest', 'EmbeddingResult']
