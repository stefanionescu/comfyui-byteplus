"""Find a typed model ID in the bundled model table and check a request against its row.

Nothing here sends a request or needs the key.
"""

import re
from ..types import Kind
from typing import Literal, overload
from collections.abc import Mapping, Sequence
from ..config.generation.models import DEFAULT_MODELS
from ..config.patterns import MODEL_ID_PATTERN, MODEL_VERSION_PATTERN
from ..types.errors import ErrorCode, BytePlusError, UnknownModelError
from ..config.models import ALIASES, KIND_NODES, MODEL_TABLE, ENDPOINT_PREFIX
from ..types.models import ChatRow, MeshRow, ImageRow, ModelRow, VideoRow, ModelMatch, MatchMethod, EmbeddingRow
from ..config.messages.models import (
    MODEL_KIND,
    MODEL_EMPTY,
    MODEL_FIELD,
    MODEL_VALUE,
    MODEL_UNKNOWN,
    MODEL_VERSION,
    MODEL_ENDPOINT,
    MODEL_UNKNOWN_ANY,
)

_MODEL_ID = re.compile(MODEL_ID_PATTERN)
VERSION_SUFFIX = re.compile(MODEL_VERSION_PATTERN)
# Each table entry holds one limits key, such as chat or video, which names the row type the entry becomes.
_ROW_TYPES: dict[str, type[ModelRow]] = {
    "chat": ChatRow,
    "image": ImageRow,
    "video": VideoRow,
    "embedding": EmbeddingRow,
    "mesh": MeshRow,
}


def _parse_rows(table: Mapping[str, Mapping[str, object]]) -> dict[str, ModelRow]:
    """Build the row of each table entry, refusing a misspelled key or a wrong value.

    The unpacking refuses an entry with no limits key or with several.
    """
    rows: dict[str, ModelRow] = {}
    for model_id, entry in table.items():
        (row_type,) = (record for key, record in _ROW_TYPES.items() if key in entry)
        rows[model_id] = row_type.model_validate({**entry, "model_id": model_id})
    return rows


# The table is parsed once, when ComfyUI imports the extension, so a mistake in it stops loading and names the key.
_ROWS = _parse_rows(MODEL_TABLE)
_EXACT_ROWS = {**_ROWS, **{alias: _ROWS[target] for alias, target in ALIASES.items()}}
# Each family, the model ID without its version, maps to its newest row, which checks an ID with an unlisted version.
# Within a family the IDs sort by version, so the newest comes last. A deprecated row always has a newer one.
_FAMILY_ROWS = {VERSION_SUFFIX.sub("", model_id): _EXACT_ROWS[model_id] for model_id in sorted(_EXACT_ROWS)}


def _describe_unknown(model_id: str, kind: Kind | None) -> str:
    """Name the model families the node takes, so the person can see which IDs it knows."""
    if kind is None:
        return MODEL_UNKNOWN_ANY.format(model=model_id)
    families = sorted(family for family, row in _FAMILY_ROWS.items() if kind in row.kinds)
    return MODEL_UNKNOWN.format(model=model_id, node=KIND_NODES[kind], families=", ".join(families))


def _find_row(model_id: str, kind: Kind | None) -> tuple[ModelRow, MatchMethod]:
    """Match the ID or a documented alias exactly, then another version of a known family.

    ModelArk needs the six-digit version, and the ID is sent as typed, so a family name alone is refused.
    """
    if not _MODEL_ID.match(model_id):
        raise UnknownModelError(ErrorCode.INVALID_INPUT, _describe_unknown(model_id, kind))
    if model_id in _EXACT_ROWS:
        return _EXACT_ROWS[model_id], "exact"
    family = VERSION_SUFFIX.sub("", model_id)
    if family not in _FAMILY_ROWS:
        raise UnknownModelError(ErrorCode.INVALID_INPUT, _describe_unknown(model_id, kind))
    row = _FAMILY_ROWS[family]
    if family == model_id:
        raise BytePlusError(ErrorCode.INVALID_INPUT, MODEL_VERSION.format(model=model_id, newest=row.model_id))
    return row, "family"


# Each overload stub's body is pass: CodeQL reports an ellipsis body as a statement with no effect.
@overload
def find_model(model_id: str, kind: Literal["chat"]) -> ModelMatch[ChatRow]:
    pass


@overload
def find_model(model_id: str, kind: Literal["images", "layers"]) -> ModelMatch[ImageRow]:
    pass


@overload
def find_model(model_id: str, kind: Literal["videos"]) -> ModelMatch[VideoRow]:
    pass


@overload
def find_model(model_id: str, kind: Literal["embeddings"]) -> ModelMatch[EmbeddingRow]:
    pass


@overload
def find_model(model_id: str, kind: Literal["meshes"]) -> ModelMatch[MeshRow]:
    pass


@overload
def find_model(model_id: str, kind: None) -> ModelMatch[ModelRow]:
    pass


def find_model(model_id: str, kind: Kind | None) -> ModelMatch[ModelRow]:
    """Find the row that checks a typed model ID for one kind of node, refusing an ID the table cannot check.

    The kind is None for Model: Info, which takes a model of any kind. An endpoint ID does not say which model it
    serves, so no row can check it. A deprecated or retiring row matches without a warning.
    """
    text = model_id.strip()
    if not text:
        raise BytePlusError(ErrorCode.INVALID_INPUT, MODEL_EMPTY)
    if text.startswith(ENDPOINT_PREFIX):
        example = DEFAULT_MODELS[kind or "chat"]
        raise BytePlusError(ErrorCode.INVALID_INPUT, MODEL_ENDPOINT.format(example=example))
    row, matched = _find_row(text, kind)
    if kind is not None and kind not in row.kinds:
        nodes = " or ".join(node for row_kind, node in KIND_NODES.items() if row_kind in row.kinds)
        message = MODEL_KIND.format(model=text, node=KIND_NODES[kind], nodes=nodes)
        raise BytePlusError(ErrorCode.INVALID_INPUT, message)
    return ModelMatch(model_id=text, row=row, matched=matched)


def validate_value(match: ModelMatch[ModelRow], label: str, value: str, values: Sequence[str]) -> None:
    """Refuse a setting the model does not take at all, or a value it does not list.

    The label is the control's label as the node shows it, such as output format. An empty list of values means the
    model takes no such setting.
    """
    if not values:
        raise BytePlusError(ErrorCode.INVALID_INPUT, MODEL_FIELD.format(model=match.model_id, field=label))
    if value not in values:
        message = MODEL_VALUE.format(model=match.model_id, field=label, values=", ".join(values))
        raise BytePlusError(ErrorCode.INVALID_INPUT, message)


__all__ = ["VERSION_SUFFIX", "find_model", "validate_value"]
