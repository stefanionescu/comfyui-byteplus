"""Find a chat model the bundled table lacks in ModelArk's model listing, so a newer chat model works without an update.

The listing bills nothing. It lists what a model reads and its token limits, but not whether it takes thinking or a
reasoning effort, or reads PDF files, so a row built from it takes none of these.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from .transport import send_lookup
from pydantic import ValidationError
from ..types.replies import ModelListReply
from ..config.byteplus import ENDPOINT_URLS
from ..types.models import ChatRow, ModelMatch
from ..types.errors import ErrorCode, BytePlusError
from ..config.messages.models import MODEL_SHUT_DOWN
from ..config.generation.chat import SAMPLING, MAX_STOP, LISTED_SHUT_DOWN, LISTED_CHAT_DOMAINS

if TYPE_CHECKING:
    from collections.abc import Mapping
    from ..types.replies import ListedModel
    from ..types.settings import Configuration

# ModelArk's listing by model ID, read on first use and kept for the ComfyUI session: it changes only when ModelArk
# releases or ends a model, so one read serves every later chat run.
_LISTED_MODELS: dict[str, ListedModel] = {}


async def _read_listing(configuration: Configuration) -> Mapping[str, ListedModel]:
    """Read the listing once and keep it; a failed read keeps nothing, so the next run reads it again."""
    if not _LISTED_MODELS:
        try:
            reply = ModelListReply.model_validate(await send_lookup(ENDPOINT_URLS["models"], configuration))
        except (BytePlusError, ValidationError):
            return {}
        _LISTED_MODELS.update((model.id, model) for model in reply.models)
    return _LISTED_MODELS


def _build_row(listed: ListedModel) -> ChatRow:
    """Build a chat row from what the listing says the model reads and takes.

    The listing names no sampling limits, so a listed model takes every sampling field and the Chat API's own number
    of stop words.
    """
    limits = listed.token_limits
    formats = listed.features.structured_outputs
    offered = {"json_schema": formats.has_schema, "json_object": formats.has_json}
    return ChatRow.model_validate(
        {
            "model_id": listed.id,
            "kinds": ("chat",),
            "inputs": listed.modalities.input_modalities,
            "sources": (),
            "chat": {
                "context": limits.context_window,
                "max_output": limits.max_output_token_length,
                "thinking": (),
                "has_effort": False,
                "sampling": dict.fromkeys(SAMPLING, "always"),
                "max_stop": MAX_STOP,
                "response_formats": tuple(name for name, is_offered in offered.items() if is_offered),
            },
        }
    )


async def find_listed_chat_model(model_id: str, configuration: Configuration) -> ModelMatch[ChatRow] | None:
    """Find a chat model in ModelArk's listing; None keeps the table's refusal.

    None when the listing cannot be read, or does not list the ID as a chat model that writes text. A model ModelArk
    has shut down is refused before anything is paid.
    """
    listed = (await _read_listing(configuration)).get(model_id)
    if listed is None or listed.domain not in LISTED_CHAT_DOMAINS or "text" not in listed.modalities.output_modalities:
        return None
    if listed.status == LISTED_SHUT_DOWN:
        raise BytePlusError(ErrorCode.INVALID_INPUT, MODEL_SHUT_DOWN.format(model=model_id))
    return ModelMatch(model_id=model_id, row=_build_row(listed), matched="listing")


__all__ = ["find_listed_chat_model"]
