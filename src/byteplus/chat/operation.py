"""Send one chat completion to ModelArk and read its answer and reasoning."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

from pydantic import ValidationError

from ..models import find_model, validate_value
from .content import build_body
from ..listing import find_listed_chat_model
from ..uploads import validate_upload_size
from ..transport import send_json
from ..references import validate_references
from ...state.chat import ChatResult
from ...state.errors import ErrorCode, BytePlusError, UnknownModelError
from ...state.models import ChatRow
from ...config.models import MEDIA_LABELS
from ...state.replies import ChatReply, ChatMessage
from ...config.byteplus import ENDPOINT_URLS
from ...config.messages.run import ANSWER_CUT, REPLY_EMPTY, ANSWER_FILTERED, REPLY_UNREADABLE
from ...config.messages.inputs import (
    PROMPT_EMPTY,
    STOP_TOO_MANY,
    SAMPLING_FIXED,
    SCHEMA_JSON_ONLY,
    STOP_UNSUPPORTED,
    SAMPLING_THINKING,
    EFFORT_UNSUPPORTED,
    SCHEMA_UNSUPPORTED,
)
from ...config.messages.models import MODEL_INPUT

if TYPE_CHECKING:
    from ...state import Json
    from ...state.chat import ChatRequest
    from ...state.models import ModelMatch
    from ...state.settings import Settings, Configuration


def _validate_inputs(request: ChatRequest, match: ModelMatch[ChatRow]) -> None:
    """Refuse a connected kind of file, local or by reference, that the model does not read."""
    linked = {reference.kind for reference in request.references}
    connected = {
        'image': bool(request.image_urls),
        'video': bool(request.video_urls),
        'audio': bool(request.audio_clips),
        'pdf': any(document.file_url for document in request.documents),
    }
    for kind, is_local in connected.items():
        if (is_local or kind in linked) and kind not in match.row.inputs:
            message = MODEL_INPUT.format(model=match.model_id, media=MEDIA_LABELS[kind])
            raise BytePlusError(ErrorCode.INVALID_INPUT, message)


def _validate_sampling(request: ChatRequest, match: ModelMatch[ChatRow], field: str) -> None:
    """Refuse a sampling field ModelArk fixes for the model, or one that takes effect only with the other thinking.

    Every model in the table reasons by default, so a field for models that do not reason needs thinking disabled.
    """
    mode = match.row.chat.sampling.get(field)
    names = {'model': match.model_id, 'field': field}
    if mode is None:
        raise BytePlusError(ErrorCode.INVALID_INPUT, SAMPLING_FIXED.format(**names))
    if mode == 'with_thinking' and request.thinking == 'disabled':
        raise BytePlusError(ErrorCode.INVALID_INPUT, SAMPLING_THINKING.format(**names, thinking='enabled'))
    if mode == 'without_thinking' and request.thinking != 'disabled':
        raise BytePlusError(ErrorCode.INVALID_INPUT, SAMPLING_THINKING.format(**names, thinking='disabled'))


def _validate_controls(request: ChatRequest, match: ModelMatch[ChatRow]) -> None:
    """Refuse a control that the model row does not take, before ModelArk bills anything.

    A model that takes only json_object makes valid JSON but ignores a schema. The check refuses a schema for such a
    model, so no answer only looks as if it followed one.
    """
    limits = match.row.chat
    if request.thinking is not None:
        validate_value(match, 'thinking', request.thinking, limits.thinking)
    if request.effort is not None and not limits.has_effort:
        raise BytePlusError(ErrorCode.INVALID_INPUT, EFFORT_UNSUPPORTED.format(model=match.model_id))
    for field in request.sampling:
        _validate_sampling(request, match, field)
    if request.stop and len(request.stop) > limits.max_stop:
        count = len(request.stop)
        names = {'model': match.model_id, 'maximum': limits.max_stop, 'count': count, 'extra': count - limits.max_stop}
        template = STOP_TOO_MANY if limits.max_stop else STOP_UNSUPPORTED
        raise BytePlusError(ErrorCode.INVALID_INPUT, template.format(**names))
    if request.json_schema is not None and 'json_schema' not in limits.response_formats:
        template = SCHEMA_JSON_ONLY if 'json_object' in limits.response_formats else SCHEMA_UNSUPPORTED
        raise BytePlusError(ErrorCode.INVALID_INPUT, template.format(model=match.model_id))


async def _find_chat_model(model_id: str, configuration: Configuration) -> ModelMatch[ChatRow]:
    """Find the model's row in the table, or else in ModelArk's model listing."""
    try:
        return find_model(model_id, 'chat', ChatRow)
    except UnknownModelError:
        match = await find_listed_chat_model(model_id, configuration)
        if match is None:
            raise
        return match


def _parse_answer(document: Json) -> ChatResult:
    """Read the answer and reasoning of the first choice.

    ModelArk stops an answer that its moderation filters without an error, so this function refuses a filtered answer
    even when some text came back. It returns the text of an answer that the token limit cut, as it is.
    """
    try:
        reply = ChatReply.model_validate(document)
    except ValidationError:
        raise BytePlusError(ErrorCode.UNCERTAIN, REPLY_UNREADABLE) from None
    if not reply.choices:
        raise BytePlusError(ErrorCode.TRANSPORT, REPLY_EMPTY)
    choice = reply.choices[0]
    if choice.finish_reason == 'content_filter':
        raise BytePlusError(ErrorCode.REFUSED, ANSWER_FILTERED)
    message = choice.message or ChatMessage()
    if not message.content:
        # Reasoning can spend the whole max_completion_tokens before the answer starts.
        if choice.finish_reason == 'length':
            raise BytePlusError(ErrorCode.INVALID_INPUT, ANSWER_CUT)
        raise BytePlusError(ErrorCode.TRANSPORT, REPLY_EMPTY)
    return ChatResult(text=message.content, reasoning=message.reasoning_content or '')


@dataclass(frozen=True, slots=True)
class ChatOperation:
    """One chat completion, sent once; ModelArk bills every token the model writes, reasoning included.

    Attributes:
        request: The request to validate and send.

    """

    request: ChatRequest

    def validate(self, settings: Settings) -> None:
        """Refuse a blank prompt, media above the maximum upload size, and references ModelArk cannot read.

        Only Seedance video reads assets, so this method refuses asset references.
        """
        request = self.request
        if not request.prompt.strip():
            raise BytePlusError(ErrorCode.INVALID_INPUT, PROMPT_EMPTY)
        files = [document.file_url for document in request.documents if document.file_url]
        validate_upload_size((*request.image_urls, *request.video_urls, *request.audio_clips, *files), settings)
        validate_references(request.references, ('image', 'video', 'audio'), can_read_assets=False)

    async def send(self, configuration: Configuration) -> ChatResult:
        """Check the request against the model's row, send it, and read the answer."""
        request = self.request
        match = await _find_chat_model(request.model_id, configuration)
        _validate_inputs(request, match)
        _validate_controls(request, match)
        body = build_body(request, match.row)
        return _parse_answer(await send_json(ENDPOINT_URLS['chat'], body, configuration))


__all__ = ['ChatOperation']
