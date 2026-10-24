"""Find a chat model the bundled table lacks in the ModelArk model listing, so a newer model works without an update.

The listing bills nothing. It lists what a model reads and its token limits. It does not say whether the model takes
thinking or a reasoning effort, or reads PDF files, so a row built from it takes none of these.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError

from .transport import send_lookup
from ..state.errors import ErrorCode, BytePlusError
from ..state.models import ChatRow, ModelMatch
from ..state.replies import ModelListReply
from ..config.byteplus import ENDPOINT_URLS
from ..config.generation.chat import MAX_STOP, SAMPLING, LISTED_SHUT_DOWN, LISTED_CHAT_DOMAINS
from ..config.messages.models import MODEL_SHUT_DOWN

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ..state.replies import ListedModel
    from ..state.settings import Configuration

# The ModelArk listing by model ID. The first use reads it, and the ComfyUI session keeps it. The listing changes
# only when ModelArk releases or ends a model, so one read serves every later chat run.
_LISTED_MODELS: dict[str, ListedModel] = {}


async def _read_listing(configuration: Configuration) -> Mapping[str, ListedModel]:
    """Read the listing once and keep it; a failed read keeps nothing, so the next run reads it again."""
    if not _LISTED_MODELS:
        try:
            reply = ModelListReply.model_validate(await send_lookup(ENDPOINT_URLS['models'], configuration))
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
    offered = {'json_schema': formats.has_schema, 'json_object': formats.has_json}
    return ChatRow.model_validate(
        {
            'model_id': listed.id,
            'kinds': ('chat',),
            'inputs': listed.modalities.input_modalities,
            'sources': (),
            'chat': {
                'context': limits.context_window,
                'max_output': limits.max_output_token_length,
                'thinking': (),
                'has_effort': False,
                'sampling': dict.fromkeys(SAMPLING, 'always'),
                'max_stop': MAX_STOP,
                'response_formats': tuple(name for name, is_offered in offered.items() if is_offered),
            },
        }
    )


async def find_listed_chat_model(model_id: str, configuration: Configuration) -> ModelMatch[ChatRow] | None:
    """Find a chat model in the ModelArk listing; None keeps the refusal of the table.

    None when the listing is unreadable, or does not list the ID as a chat model that writes text. This function
    refuses a model that ModelArk has shut down, before ModelArk bills anything.
    """
    listed = (await _read_listing(configuration)).get(model_id)
    if listed is None or listed.domain not in LISTED_CHAT_DOMAINS or 'text' not in listed.modalities.output_modalities:
        return None
    if listed.status == LISTED_SHUT_DOWN:
        raise BytePlusError(ErrorCode.INVALID_INPUT, MODEL_SHUT_DOWN.format(model=model_id))
    return ModelMatch(model_id=model_id, row=_build_row(listed), matched='listing')


__all__ = ['find_listed_chat_model']
