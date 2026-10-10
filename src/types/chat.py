"""Chat documents, conversations, requests, and results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from . import Json
    from .options import Options
    from .references import Reference
    from collections.abc import Mapping


@dataclass(frozen=True, slots=True)
class Document:
    """One file attached to a chat request.

    Attributes:
        name: The file name the model sees.
        media_type: The file's media type.
        text: The contents of a text file.
        file_url: A PDF as a data URL.

    """

    name: str
    media_type: str
    text: str | None
    file_url: str | None


@dataclass(frozen=True, slots=True)
class Turn:
    """One message of an earlier exchange.

    Attributes:
        role: Who wrote the message.
        text: What the message says.

    """

    role: Literal["user", "assistant"]
    text: str


@dataclass(frozen=True, slots=True)
class Conversation:
    """The turns before the next question, oldest first.

    Attributes:
        turns: The earlier messages.

    """

    turns: tuple[Turn, ...]


@dataclass(frozen=True, slots=True)
class ChatRequest:
    """One chat completion with its media already encoded; None means model default.

    Attributes:
        model_id: The model ID sent to ModelArk.
        system_prompt: System instructions, sent when not blank.
        prompt: The question.
        conversation: Earlier turns sent before the question.
        image_urls: PNG data URLs.
        video_urls: MP4 data URLs.
        audio_clips: Base64 WAV without a data: prefix, as the input_audio part takes it.
        documents: Attached files, in chain order.
        references: Image, video, and audio addresses ModelArk reads itself, in chain order.
        thinking: The thinking.type to send, enabled or disabled.
        effort: The reasoning effort to send.
        max_tokens: The most tokens the model may write, reasoning included, or 0 for ModelArk's answer limit.
        temperature: The sampling temperature to send.
        answer_schema: JSON schema the answer must follow, or None for free text.
        options: The service tier and extra fields from Request Options.

    """

    model_id: str
    system_prompt: str
    prompt: str
    conversation: Conversation
    image_urls: tuple[str, ...]
    video_urls: tuple[str, ...]
    audio_clips: tuple[str, ...]
    documents: tuple[Document, ...]
    references: tuple[Reference, ...]
    thinking: str | None
    effort: str | None
    max_tokens: int
    temperature: float | None
    answer_schema: Mapping[str, Json] | None
    options: Options | None


@dataclass(frozen=True, slots=True)
class ChatResult:
    """What one chat completion returned.

    Attributes:
        text: The answer.
        reasoning: The model's reasoning, or a summary of it, when it shares one.

    """

    text: str
    reasoning: str


__all__ = ["ChatRequest", "ChatResult", "Conversation", "Document", "Turn"]
