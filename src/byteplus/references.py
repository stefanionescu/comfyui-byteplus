"""Parse, check, and order the files ModelArk reads by address, so every node applies the same reference rules."""

import re
from ..types import Json
from urllib.parse import urlsplit
from datetime import datetime, timedelta
from ..config.units import SECONDS_PER_MINUTE
from ..config.patterns import ASSET_ID_PATTERN
from collections.abc import Sequence, Collection
from ..types.errors import ErrorCode, ByteplusError
from ..types.references import Reference, ReferenceKind
from ..config.messages.references import (
    REFERENCE_KIND,
    REFERENCE_ASSET,
    REFERENCE_SOURCE,
    REFERENCE_EXPIRED,
    REFERENCE_SOURCE_EMPTY,
    REFERENCE_DRAFT_EXPIRED,
    REFERENCE_ADDRESS_LENGTH,
)
from ..config.generation.references import (
    PART_TYPES,
    LINK_SCHEME,
    REFERENCE_KINDS,
    REFERENCE_ROLES,
    ASSET_URI_PREFIX,
    EXPIRY_MARGIN_SECONDS,
    MAX_ADDRESS_CHARACTERS,
)

# BytePlus's API reference writes "Asset-…" and its Playground "asset-…", so the case does not matter.
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


def parse_reference_source(source: str, kind: ReferenceKind) -> Reference:
    """Parse what a person typed into Reference: Add: an asset ID, an asset:// URI, or a public https address.

    The asset ID is kept exactly as typed, since BytePlus treats IDs as opaque. Any other text, such as an http://
    or data: address, is refused.
    """
    text = source.strip()
    if not text:
        raise ByteplusError(ErrorCode.INVALID_INPUT, REFERENCE_SOURCE_EMPTY)
    if len(text) > MAX_ADDRESS_CHARACTERS:
        raise ByteplusError(ErrorCode.INVALID_INPUT, REFERENCE_ADDRESS_LENGTH.format(maximum=MAX_ADDRESS_CHARACTERS))
    match = _ASSET_ID.match(text)
    if match is not None:
        return Reference(kind, ASSET_URI_PREFIX + match.group(1), "asset", None)
    if _is_link(text):
        return Reference(kind, text, "link", None)
    raise ByteplusError(ErrorCode.INVALID_INPUT, REFERENCE_SOURCE)


def validate_references(
    references: Sequence[Reference],
    kinds: Collection[ReferenceKind],
    *,
    can_read_assets: bool,
    now: datetime,
) -> None:
    """Refuse a reference the node's model cannot read, or one that expires before ModelArk may read it.

    Every model reads outputs and links, so assets are the only origin a model refuses. ModelArk may read a reference
    only when a queued task starts, so an output must last a margin beyond now. Counting references against the
    model's limits is the caller's check.
    """
    deadline = now + timedelta(seconds=EXPIRY_MARGIN_SECONDS)
    for position, reference in enumerate(references, start=1):
        if reference.kind not in kinds:
            names = ", ".join(kind for kind in REFERENCE_KINDS if kind in kinds)
            message = REFERENCE_KIND.format(kinds=names, position=position, kind=reference.kind)
            raise ByteplusError(ErrorCode.INVALID_INPUT, message)
        if reference.origin == "asset" and not can_read_assets:
            raise ByteplusError(ErrorCode.INVALID_INPUT, REFERENCE_ASSET.format(position=position))
        if reference.expires_at is not None and reference.expires_at < deadline:
            template = REFERENCE_DRAFT_EXPIRED if reference.kind == "draft" else REFERENCE_EXPIRED
            message = template.format(position=position, minutes=EXPIRY_MARGIN_SECONDS // SECONDS_PER_MINUTE)
            raise ByteplusError(ErrorCode.INVALID_INPUT, message)


def build_reference_parts(references: Sequence[Reference]) -> tuple[dict[str, Json], ...]:
    """Build one Seedance content item per reference, in chain order; a draft item names its task and has no role."""
    parts: list[dict[str, Json]] = []
    for reference in references:
        part_type = PART_TYPES[reference.kind]
        if reference.kind == "draft":
            parts.append({"type": part_type, part_type: {"id": reference.address}})
        else:
            address: dict[str, Json] = {"url": reference.address}
            parts.append({"type": part_type, part_type: address, "role": REFERENCE_ROLES[reference.kind]})
    return tuple(parts)


__all__ = ["build_reference_parts", "parse_reference_source", "validate_references"]
