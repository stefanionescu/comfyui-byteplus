"""Parse, check, and build the files ModelArk reads by address, so every node applies the same reference rules."""

import re
from urllib.parse import urlsplit
from collections.abc import Sequence
from ..config.units import SECONDS_PER_MINUTE
from datetime import UTC, datetime, timedelta
from ..config.patterns import ASSET_ID_PATTERN
from ..types.errors import ErrorCode, BytePlusError
from ..types.references import Reference, ReferenceKind
from ..config.messages.references import (
    REFERENCE_URL,
    REFERENCE_KIND,
    REFERENCE_ASSET,
    REFERENCE_EXPIRED,
    REFERENCE_URL_EMPTY,
    REFERENCE_DRAFT_EXPIRED,
    REFERENCE_ADDRESS_LENGTH,
)
from ..config.generation.references import (
    LINK_SCHEME,
    ASSET_URI_PREFIX,
    EXPIRY_MARGIN_SECONDS,
    DRAFT_LIFETIME_SECONDS,
    MAX_ADDRESS_CHARACTERS,
    OUTPUT_LIFETIME_SECONDS,
)

_ASSET_ID = re.compile(ASSET_ID_PATTERN, re.IGNORECASE)


def _is_link(text: str) -> bool:
    """Tell whether text is an https address with a host, no user name or password, and no whitespace.

    The scheme comes back from the split in lowercase.
    """
    if any(character.isspace() for character in text):
        return False
    try:
        parts = urlsplit(text)
    except ValueError:
        return False
    return parts.scheme == LINK_SCHEME and bool(parts.hostname) and parts.username is None and parts.password is None


def parse_reference_url(url: str, kind: ReferenceKind) -> Reference:
    """Parse what a person typed into Reference: Add: an asset ID, an asset:// URI, or a public https address.

    The asset ID is kept exactly as typed, since BytePlus treats IDs as opaque. Any other text, such as an http://
    or data: address, is refused.
    """
    text = url.strip()
    if not text:
        raise BytePlusError(ErrorCode.INVALID_INPUT, REFERENCE_URL_EMPTY)
    if len(text) > MAX_ADDRESS_CHARACTERS:
        raise BytePlusError(ErrorCode.INVALID_INPUT, REFERENCE_ADDRESS_LENGTH.format(maximum=MAX_ADDRESS_CHARACTERS))
    match = _ASSET_ID.match(text)
    if match is not None:
        return Reference(kind, ASSET_URI_PREFIX + match.group(1), "asset", None)
    if _is_link(text):
        return Reference(kind, text, "link", None)
    raise BytePlusError(ErrorCode.INVALID_INPUT, REFERENCE_URL)


def validate_references(
    references: Sequence[Reference],
    kinds: Sequence[ReferenceKind],
    *,
    can_read_assets: bool,
) -> None:
    """Refuse a reference the node's model cannot read, or one that expires before ModelArk may read it.

    Every model reads outputs and links, so assets are the only origin a model refuses. ModelArk may read a reference
    only when a queued task starts, so an output must last a margin beyond now.
    """
    deadline = datetime.now(UTC) + timedelta(seconds=EXPIRY_MARGIN_SECONDS)
    for position, reference in enumerate(references, start=1):
        if reference.kind not in kinds:
            message = REFERENCE_KIND.format(kinds=", ".join(kinds), position=position, kind=reference.kind)
            raise BytePlusError(ErrorCode.INVALID_INPUT, message)
        if reference.origin == "asset" and not can_read_assets:
            raise BytePlusError(ErrorCode.INVALID_INPUT, REFERENCE_ASSET.format(position=position))
        if reference.expires_at is not None and reference.expires_at < deadline:
            template = REFERENCE_DRAFT_EXPIRED if reference.kind == "draft" else REFERENCE_EXPIRED
            message = template.format(position=position, minutes=EXPIRY_MARGIN_SECONDS // SECONDS_PER_MINUTE)
            raise BytePlusError(ErrorCode.INVALID_INPUT, message)


def build_output_reference(kind: ReferenceKind, address: str, created_at: int) -> Reference:
    """Build the reference to a file ModelArk made, which expires with its address.

    The lifetime counts from when ModelArk accepted the request, so a reference expires a little before its address
    does, never after. A draft lasts 7 days, and every other output 24 hours.
    """
    lifetime = DRAFT_LIFETIME_SECONDS if kind == "draft" else OUTPUT_LIFETIME_SECONDS
    expires_at = datetime.fromtimestamp(created_at, UTC) + timedelta(seconds=lifetime)
    return Reference(kind, address, "output", expires_at)


__all__ = ["build_output_reference", "parse_reference_url", "validate_references"]
