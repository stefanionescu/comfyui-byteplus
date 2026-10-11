"""Find a typed model ID in the bundled model table and check a request against its row.

Nothing here sends a request or needs the key.
"""

import re
from ..types import Kind
from typing import Literal, overload
from ..types.errors import ErrorCode, ByteplusError
from ..config.generation.models import DEFAULT_MODELS
from collections.abc import Mapping, Iterable, Sequence
from ..config.patterns import MODEL_ID_PATTERN, MODEL_VERSION_PATTERN
from ..config.models import ALIASES, FAMILIES, KIND_NODES, MODEL_TABLE, MEDIA_LABELS, ENDPOINT_PREFIX
from ..types.models import ChatRow, MeshRow, ImageRow, ModelRow, VideoRow, ModelMatch, MatchMethod, EmbeddingRow
from ..config.messages.models import (
    MODEL_KIND,
    MODEL_EMPTY,
    MODEL_FIELD,
    MODEL_INPUT,
    MODEL_RANGE,
    MODEL_VALUE,
    MODEL_UNKNOWN,
    MODEL_VERSION,
    MODEL_ENDPOINT,
    MODEL_RANGE_EXTRA,
    MODEL_UNKNOWN_ANY,
)

_MODEL_ID = re.compile(MODEL_ID_PATTERN)
_MODEL_VERSION = re.compile(MODEL_VERSION_PATTERN)
# The limits key a row literal holds names the row record it becomes.
_ROW_TYPES: dict[str, type[ModelRow]] = {
    "chat": ChatRow,
    "image": ImageRow,
    "video": VideoRow,
    "embedding": EmbeddingRow,
    "mesh": MeshRow,
}


def _parse_row(model_id: str, literal: Mapping[str, object]) -> ModelRow:
    """Build the row record of one table literal, refusing a misspelled key or a wrong value.

    A literal holds exactly one limits key; unpacking refuses a literal with none or several.
    """
    family = _MODEL_VERSION.sub("", model_id)
    (row_type,) = (record for key, record in _ROW_TYPES.items() if key in literal)
    return row_type.model_validate({**literal, "model_id": model_id, "family": family})


# The table is parsed once, when ComfyUI imports the extension, so a mistake in it stops loading and names the key.
_ROWS = {model_id: _parse_row(model_id, literal) for model_id, literal in MODEL_TABLE.items()}
_EXACT_ROWS = {**_ROWS, **{alias: _ROWS[target] for alias, target in ALIASES.items()}}
_FAMILY_ROWS = {family: _ROWS[newest] for family, newest in FAMILIES.items()}


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
        raise ByteplusError(ErrorCode.INVALID_INPUT, _describe_unknown(model_id, kind))
    if model_id in _EXACT_ROWS:
        return _EXACT_ROWS[model_id], "exact"
    family = _MODEL_VERSION.sub("", model_id)
    if family not in _FAMILY_ROWS:
        raise ByteplusError(ErrorCode.INVALID_INPUT, _describe_unknown(model_id, kind))
    row = _FAMILY_ROWS[family]
    if family == model_id:
        raise ByteplusError(ErrorCode.INVALID_INPUT, MODEL_VERSION.format(model=model_id, newest=row.model_id))
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
        raise ByteplusError(ErrorCode.INVALID_INPUT, MODEL_EMPTY)
    if text.startswith(ENDPOINT_PREFIX):
        example = DEFAULT_MODELS[kind or "chat"]
        raise ByteplusError(ErrorCode.INVALID_INPUT, MODEL_ENDPOINT.format(example=example))
    row, matched = _find_row(text, kind)
    if kind is not None and kind not in row.kinds:
        nodes = " or ".join(node for row_kind, node in KIND_NODES.items() if row_kind in row.kinds)
        message = MODEL_KIND.format(model=text, node=KIND_NODES[kind], nodes=nodes)
        raise ByteplusError(ErrorCode.INVALID_INPUT, message)
    return ModelMatch(model_id=text, row=row, matched=matched, kind=kind)


def validate_model(match: ModelMatch[ModelRow], kinds: Iterable[str]) -> None:
    """Refuse each connected kind of input the model does not read: text, image, video, audio, or pdf."""
    for kind in kinds:
        if kind not in match.row.inputs:
            message = MODEL_INPUT.format(model=match.model_id, media=MEDIA_LABELS[kind])
            raise ByteplusError(ErrorCode.INVALID_INPUT, message)


def validate_value(match: ModelMatch[ModelRow], label: str, value: str, values: Sequence[str]) -> None:
    """Refuse a setting the model does not take at all, or a value it does not list.

    The label is the control's label as the node shows it, such as size; no values means the model takes no such
    setting.
    """
    if not values:
        raise ByteplusError(ErrorCode.INVALID_INPUT, MODEL_FIELD.format(model=match.model_id, field=label))
    if value not in values:
        message = MODEL_VALUE.format(model=match.model_id, field=label, values=", ".join(values))
        raise ByteplusError(ErrorCode.INVALID_INPUT, message)


def validate_range(
    match: ModelMatch[ModelRow], label: str, value: int, bounds: tuple[int, int], extra_values: Sequence[int] = ()
) -> None:
    """Refuse a number outside the model's bounds that is not one of its extra values, such as -1 for duration."""
    minimum, maximum = bounds
    if minimum <= value <= maximum or value in extra_values:
        return
    fields = {"model": match.model_id, "field": label, "minimum": minimum, "maximum": maximum}
    if extra_values:
        message = MODEL_RANGE_EXTRA.format(**fields, extra=" or ".join(str(extra) for extra in extra_values))
    else:
        message = MODEL_RANGE.format(**fields)
    raise ByteplusError(ErrorCode.INVALID_INPUT, message)


__all__ = ["find_model", "validate_model", "validate_range", "validate_value"]
