"""Files at ModelArk addresses: a reference the references socket carries, and a file ModelArk made."""

from typing import Literal
from datetime import datetime
from dataclasses import dataclass

type ReferenceKind = Literal['image', 'video', 'audio', 'draft']
type ReferenceOrigin = Literal['output', 'asset', 'link']


@dataclass(frozen=True, slots=True)
class Reference:
    """One file ModelArk reads by address.

    Attributes:
        kind: image, video, audio, or draft.
        address: An https address, an `asset://` address, or, for a draft, a video task ID.
        origin: `output` for a file ModelArk made, `asset` for a file in an asset library, or `link` for an address
            the person gave.
        expires_at: When an output stops working, in UTC; None for assets and links.

    """

    kind: ReferenceKind
    address: str
    origin: ReferenceOrigin
    expires_at: datetime | None


@dataclass(frozen=True, slots=True)
class OutputFile:
    """One file ModelArk made.

    Attributes:
        content: The downloaded file.
        address: The https address that the extension downloaded it from.

    """

    content: bytes
    address: str


# Other modules import type aliases by name; __all__ lists runtime names.
__all__ = ['OutputFile', 'Reference']
