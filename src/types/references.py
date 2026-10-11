"""Files at ModelArk addresses: a reference the references socket carries, and a file ModelArk made."""

from typing import Literal
from datetime import datetime
from dataclasses import dataclass

type ReferenceKind = Literal["image", "video", "audio", "draft"]
type ReferenceOrigin = Literal["output", "asset", "link"]


@dataclass(frozen=True, slots=True)
class Reference:
    """One file ModelArk reads by address.

    Attributes:
        kind: image, video, audio, or draft.
        address: An https address, an asset:// URI, or, for a draft, a video task ID.
        origin: output (made by ModelArk), asset (in an asset library), or link (an address the person gave).
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
        address: The https address it was downloaded from.

    """

    content: bytes
    address: str


# Type aliases are imported by name; __all__ lists runtime names.
__all__ = ["OutputFile", "Reference"]
