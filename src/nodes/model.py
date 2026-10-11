"""Report the model table row the paid nodes check a model ID against; it reads only the bundled table."""

from __future__ import annotations

import json
from comfy_api.latest import io
from ..types.models import ModelRow
from typing import override, TYPE_CHECKING
from ..config.namespace import NODE_PREFIX, MENUS
from ..config.generation.models import DEFAULT_MODELS
from ..byteplus.models import VERSION_SUFFIX, find_model
from ..config.generation.inputs import INPUT_NAMES, MODEL_TOOLTIP
from ..config.models import KIND_NAMES, DOC_PAGE_URL, SOURCE_DATES

if TYPE_CHECKING:
    from ..types.models import ModelMatch


def _format_report(match: ModelMatch[ModelRow]) -> str:
    """Write the row as JSON: the nodes that take the model, its family, what it reads, its limits, and its sources."""
    row = match.row
    # Each row record adds one field to the shared ones: the limits record of its kind, such as chat or video.
    (limits,) = row.model_dump(mode="json", exclude=set(ModelRow.model_fields)).values()
    report = {
        "model": match.model_id,
        "row": row.model_id,
        "matched": match.matched,
        "kinds": [name for kind, name in KIND_NAMES.items() if kind in row.kinds],
        "family": VERSION_SUFFIX.sub("", row.model_id),
        "status": row.status,
        "deactivation": row.deactivation,
        "replacement": row.replacement,
        "inputs": sorted(row.inputs),
        "flex": row.has_flex,
        "limits": limits,
        "sources": [{"page": DOC_PAGE_URL.format(page=page), "updated": SOURCE_DATES[page]} for page in row.sources],
    }
    return json.dumps(report, ensure_ascii=False)


class ModelInfo(io.ComfyNode):
    """Report one model's table row; it reads only the bundled table, so it needs no key and costs nothing."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the model ID and the JSON the node returns."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Model: Info",
            category=MENUS["SHARED"],
            description="Show what any BytePlus model reads, makes, and takes, as JSON. Free, and needs no key.",
            inputs=[io.String.Input(INPUT_NAMES["MODEL"], default=DEFAULT_MODELS["chat"], tooltip=MODEL_TOOLTIP)],
            outputs=[io.String.Output("info", display_name="info")],
        )

    @classmethod
    @override
    def execute(cls, *, model: str) -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        """Find the row with the paid nodes' own lookup, so this node refuses the IDs they refuse."""
        return io.NodeOutput(_format_report(find_model(model, None)))


__all__ = ["ModelInfo"]
