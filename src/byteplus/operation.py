"""Define the paid request every node hands to the run wrapper, and measure and limit the media it sends."""

from __future__ import annotations

import math
from typing import Protocol, TYPE_CHECKING
from ..config.units import BYTES_PER_MEBIBYTE
from ..config.messages.media import UPLOAD_LIMIT
from ..types.errors import ErrorCode, BytePlusError

if TYPE_CHECKING:
    from collections.abc import Iterable
    from ..types.settings import Settings, Configuration


class Operation[Result](Protocol):
    """One paid ModelArk request, validated before it is sent."""

    def validate(self, settings: Settings) -> None:
        """Refuse inputs the settings or the endpoint do not allow, before anything is sent."""
        raise NotImplementedError(settings)

    async def send(self, configuration: Configuration) -> Result:
        """Send the request and return its parsed result."""
        raise NotImplementedError(configuration)


def validate_upload_size(media: Iterable[str], settings: Settings) -> None:
    """Refuse encoded media, data URLs or base64 text, larger in total than the maximum upload size."""
    size = sum(len(item) for item in media)
    if size > settings.max_upload_megabytes * BYTES_PER_MEBIBYTE:
        shown = math.ceil(size * 10 / BYTES_PER_MEBIBYTE) / 10
        raise BytePlusError(
            ErrorCode.INVALID_INPUT, UPLOAD_LIMIT.format(size=shown, maximum=settings.max_upload_megabytes)
        )


def measure_encoded_bytes(encoded: str) -> int:
    """Measure the file a data URL or a base64 text holds, without decoding it.

    ModelArk's per-file limits count the file, not its base64 text, which is a third longer.
    """
    _, comma, tail = encoded.partition(",")
    text = tail if comma else encoded
    padding = len(text) - len(text.rstrip("="))
    return len(text) * 3 // 4 - padding


__all__ = ["Operation", "measure_encoded_bytes", "validate_upload_size"]
