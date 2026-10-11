"""Choose the service tier and extra request fields once, for any number of BytePlus nodes."""

from __future__ import annotations

from comfy_api.latest import io
from types import MappingProxyType
from ..types.options import Options
from ..types.parsing import parse_json
from typing import override, TYPE_CHECKING
from ..config.messages.inputs import OPTIONS_JSON
from ..types.errors import ErrorCode, ByteplusError
from ..config.generation.inputs import MODEL_DEFAULT
from ..config.generation.options import TIER_CHOICES
from ..config.namespace import NODE_PREFIX, MENUS, SOCKET_TYPES

if TYPE_CHECKING:
    from ..types import Json


def _parse_fields(text: str, field: str) -> dict[str, Json]:
    """Parse a JSON object field, or nothing when it is empty."""
    if not text.strip():
        return {}
    try:
        value = parse_json(text)
    except ByteplusError:
        value = None
    if not isinstance(value, dict):
        raise ByteplusError(ErrorCode.INVALID_INPUT, OPTIONS_JSON.format(field=field))
    return value


class RequestOptions(io.ComfyNode):
    """Output the service tier and extra fields; the paid node refuses what its request or model does not take."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Offer the service tier, model default or flex, and the extra fields as one JSON object."""
        tier = io.Combo.Input(
            "service_tier",
            display_name="service tier",
            options=list(TIER_CHOICES),
            default=MODEL_DEFAULT,
            tooltip="flex asks for ModelArk's lower-cost tier, which queues requests until it has room. Only some "
            "chat and Seedance 1.x models take it; Model: Info shows which.",
        )
        extra_fields = io.String.Input(
            "extra_fields",
            display_name="extra fields",
            placeholder="extra fields",
            multiline=True,
            default="",
            advanced=True,
            tooltip="A JSON object of request fields, added to the request as written. The node refuses a field it "
            "sets itself.",
        )
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Request Options",
            category=MENUS["SHARED"],
            description="Choose the service tier and extra request fields for any BytePlus node.",
            inputs=[tier, extra_fields],
            outputs=[io.Custom(SOCKET_TYPES["OPTIONS"]).Output("options", display_name="options")],
        )

    @classmethod
    @override
    def execute(cls, *, service_tier: str, extra_fields: str) -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        """Check the extra fields before any request; a paid node checks the rest when it merges them."""
        options = Options(
            tier=None if service_tier == MODEL_DEFAULT else service_tier,
            extra_fields=MappingProxyType(_parse_fields(extra_fields, "extra fields")),
        )
        return io.NodeOutput(options)


__all__ = ["RequestOptions"]
