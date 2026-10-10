"""Merge the tier and extra fields of a Request Options node into one request body."""

from __future__ import annotations

from typing import TYPE_CHECKING
from ..config.models import KIND_NODES
from ..types.errors import ErrorCode, ByteplusError
from ..config.byteplus import TIERS, RESERVED_FIELDS
from ..config.messages.inputs import OPTION_FLEX, OPTION_TIER_KIND, OPTION_RESERVED_FIELD

if TYPE_CHECKING:
    from ..types import Json, Kind
    from ..types.models import ModelRow
    from ..types.options import Options
    from collections.abc import Mapping


def build_request_body(body: Mapping[str, Json], options: Options | None, kind: Kind, row: ModelRow) -> dict[str, Json]:
    """Add the options' extra fields and tier, refusing before anything is sent what this request cannot take.

    Extra fields go at the top level as written and may replace a field the node set, such as watermark, but never one
    it reserves. The tier is refused for a kind of request that takes none, and flex for a model whose row lacks it.
    """
    merged = dict(body)
    if options is None:
        return merged
    for field in options.extra_fields:
        if field in RESERVED_FIELDS[kind]:
            raise ByteplusError(ErrorCode.INVALID_INPUT, OPTION_RESERVED_FIELD.format(field=field))
    merged.update(options.extra_fields)
    if options.tier is not None:
        if options.tier not in TIERS.get(kind, ()):
            raise ByteplusError(ErrorCode.INVALID_INPUT, OPTION_TIER_KIND.format(node=KIND_NODES[kind]))
        if not row.has_flex:
            raise ByteplusError(ErrorCode.INVALID_INPUT, OPTION_FLEX.format(model=row.model_id))
        merged["service_tier"] = options.tier
    return merged


__all__ = ["build_request_body"]
