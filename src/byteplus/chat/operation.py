"""Send one chat completion to ModelArk and read its answer and reasoning."""

from __future__ import annotations

import math
from .content import build_body
from typing import TYPE_CHECKING
from ..transport import send_json
from datetime import UTC, datetime
from ...types.chat import ChatResult
from pydantic import ValidationError
from ...config.byteplus import ENDPOINT_URLS
from ..listing import find_listed_chat_model
from ..references import validate_references
from ...config.units import BYTES_PER_MEGABYTE
from ...types.replies import ChatReply, ChatMessage
from ...types.errors import ErrorCode, ByteplusError
from ..models import find_model, validate_model, validate_value
from ..operation import validate_upload_size, measure_encoded_bytes
from ...config.messages.run import ANSWER_CUT, REPLY_EMPTY, ANSWER_FILTERED, REPLY_UNREADABLE
from ...config.generation.chat import MEDIA_BYTES, THINKING_OFF, MAX_BODY_BYTES, THINKING_OFF_EFFORT
from ...config.messages.inputs import (
    PROMPT_EMPTY,
    CHAT_PDF_SIZE,
    CHAT_BODY_SIZE,
    CHAT_AUDIO_SIZE,
    CHAT_IMAGE_SIZE,
    CHAT_VIDEO_SIZE,
    SCHEMA_JSON_ONLY,
    TEMPERATURE_FIXED,
    EFFORT_UNSUPPORTED,
    SCHEMA_UNSUPPORTED,
    OUTPUT_TOKENS_RANGE,
    EFFORT_WITHOUT_THINKING,
)

if TYPE_CHECKING:
    from ...types import Json
    from ...types.chat import ChatRequest
    from ...types.models import ChatRow, ModelMatch
    from ...types.settings import Settings, Configuration

# The refusal of a file above ModelArk's limit for its kind.
_FILE_SIZE_MESSAGES = {
    "image": CHAT_IMAGE_SIZE,
    "video": CHAT_VIDEO_SIZE,
    "audio": CHAT_AUDIO_SIZE,
    "pdf": CHAT_PDF_SIZE,
}


def _list_files(request: ChatRequest) -> list[tuple[str, str, str]]:
    """List every encoded file with its kind and, for a PDF, its name: the images, videos, audio, then the PDFs."""
    files = [("image", url, "") for url in request.image_urls]
    files += [("video", url, "") for url in request.video_urls]
    files += [("audio", clip, "") for clip in request.audio_clips]
    files += [("pdf", document.file_url, document.name) for document in request.documents if document.file_url]
    return files


def _validate_file_sizes(request: ChatRequest, files: list[tuple[str, str, str]]) -> None:
    """Refuse a file above ModelArk's limit for its kind, and files that make the request body too large.

    ModelArk's per-file limits count the file, not its base64 text; its body limit counts what is sent.
    """
    for kind, encoded, name in files:
        size = measure_encoded_bytes(encoded)
        if size > MEDIA_BYTES[kind]:
            shown = math.ceil(size * 10 / BYTES_PER_MEGABYTE) / 10
            raise ByteplusError(ErrorCode.INVALID_INPUT, _FILE_SIZE_MESSAGES[kind].format(size=shown, name=name))
    texts = sum(len(document.text.encode()) for document in request.documents if document.text is not None)
    total = sum(len(encoded) for _kind, encoded, _name in files) + texts
    if total > MAX_BODY_BYTES:
        shown = math.ceil(total * 10 / BYTES_PER_MEGABYTE) / 10
        raise ByteplusError(ErrorCode.INVALID_INPUT, CHAT_BODY_SIZE.format(size=shown))


def _list_input_kinds(request: ChatRequest) -> list[str]:
    """List the kinds of file connected, local or by reference, in a fixed order; a text document needs no kind."""
    linked = {reference.kind for reference in request.references}
    connected = {
        "image": bool(request.image_urls),
        "video": bool(request.video_urls),
        "audio": bool(request.audio_clips),
        "pdf": any(document.file_url for document in request.documents),
    }
    return [kind for kind, is_local in connected.items() if is_local or kind in linked]


def _validate_thinking(request: ChatRequest, match: ModelMatch[ChatRow]) -> None:
    """Refuse a thinking.type the model's row does not list, and an effort choice the model does not take.

    With thinking disabled, ModelArk returns an error for any effort but minimal.
    """
    limits = match.row.chat
    if request.thinking is not None:
        validate_value(match, "thinking", request.thinking, limits.thinking)
    if request.effort is not None and not limits.has_effort:
        raise ByteplusError(ErrorCode.INVALID_INPUT, EFFORT_UNSUPPORTED.format(model=match.model_id))
    if request.thinking == THINKING_OFF and request.effort not in {None, THINKING_OFF_EFFORT}:
        raise ByteplusError(ErrorCode.INVALID_INPUT, EFFORT_WITHOUT_THINKING)


def _validate_controls(request: ChatRequest, match: ModelMatch[ChatRow]) -> None:
    """Refuse, before anything is paid, a control the model's row does not take; the first refusal stops the check.

    A model that takes only json_object makes valid JSON but ignores a schema, so it refuses one rather than look
    as if it followed it.
    """
    limits = match.row.chat
    _validate_thinking(request, match)
    if request.temperature is not None and not limits.has_temperature:
        raise ByteplusError(ErrorCode.INVALID_INPUT, TEMPERATURE_FIXED.format(model=match.model_id))
    if request.json_schema is not None and "json_schema" not in limits.answer_formats:
        template = SCHEMA_JSON_ONLY if "json_object" in limits.answer_formats else SCHEMA_UNSUPPORTED
        raise ByteplusError(ErrorCode.INVALID_INPUT, template.format(model=match.model_id))
    if request.max_completion_tokens > limits.max_output:
        message = OUTPUT_TOKENS_RANGE.format(model=match.model_id, maximum=limits.max_output)
        raise ByteplusError(ErrorCode.INVALID_INPUT, message)


async def _find_chat_model(model_id: str, configuration: Configuration) -> ModelMatch[ChatRow]:
    """Find the model's row in the table, or else in ModelArk's model listing.

    The listing holds chat models newer than the table. When it does not list the ID as one, the table's refusal
    stands.
    """
    try:
        return find_model(model_id, "chat")
    except ByteplusError:
        match = await find_listed_chat_model(model_id, configuration)
        if match is None:
            raise
        return match


def _parse_answer(document: Json) -> ChatResult:
    """Read the first choice's answer and reasoning.

    ModelArk stops an answer its moderation filters without an error, so a filtered answer is refused even when some
    text came back. An answer cut at the token limit with text is returned as it is.
    """
    try:
        reply = ChatReply.model_validate(document)
    except ValidationError:
        raise ByteplusError(ErrorCode.UNCERTAIN, REPLY_UNREADABLE) from None
    if not reply.choices:
        raise ByteplusError(ErrorCode.TRANSPORT, REPLY_EMPTY)
    choice = reply.choices[0]
    if choice.finish_reason == "content_filter":
        raise ByteplusError(ErrorCode.REFUSED, ANSWER_FILTERED)
    message = choice.message or ChatMessage()
    if not message.content:
        # Reasoning can spend the whole max_completion_tokens before the answer starts.
        if choice.finish_reason == "length":
            raise ByteplusError(ErrorCode.INVALID_INPUT, ANSWER_CUT)
        raise ByteplusError(ErrorCode.TRANSPORT, REPLY_EMPTY)
    return ChatResult(text=message.content, reasoning=message.reasoning_content or "")


class ChatOperation:
    """One chat completion, sent once; ModelArk bills every token the model writes, reasoning included."""

    def __init__(self, request: ChatRequest) -> None:
        """Keep the request to validate and send."""
        self.request = request

    def validate(self, settings: Settings) -> None:
        """Refuse a blank prompt, files above ModelArk's limits or the maximum upload size, and unreadable references.

        Only Seedance video reads assets, so asset references are refused.
        """
        request = self.request
        if not request.prompt.strip():
            raise ByteplusError(ErrorCode.INVALID_INPUT, PROMPT_EMPTY)
        files = _list_files(request)
        _validate_file_sizes(request, files)
        validate_upload_size((encoded for _kind, encoded, _name in files), settings)
        validate_references(
            request.references, frozenset({"image", "video", "audio"}), can_read_assets=False, now=datetime.now(UTC)
        )

    async def send(self, configuration: Configuration) -> ChatResult:
        """Check the request against the model's row, send it, and read the answer."""
        request = self.request
        match = await _find_chat_model(request.model_id, configuration)
        validate_model(match, _list_input_kinds(request))
        _validate_controls(request, match)
        body = build_body(request, match.row)
        return _parse_answer(await send_json(ENDPOINT_URLS["chat"], body, configuration))


__all__ = ["ChatOperation"]
