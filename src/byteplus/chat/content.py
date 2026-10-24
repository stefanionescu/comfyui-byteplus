"""Build a chat completion's messages and body from one chat request."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..options import build_request_body
from ...config.media import WAV
from ...config.generation.chat import DOCUMENT_TEXT

if TYPE_CHECKING:
    from ...state import Json
    from ...state.chat import ChatRequest
    from ...state.models import ModelRow


def _build_parts(request: ChatRequest) -> list[Json]:
    """List the question's parts: the documents, images, videos, and audio, then the prompt.

    ModelArk's guides put the text after the media. Within each kind, the local files come first, then the references
    in chain order. A text document goes as text, so a model that reads no files reads it too. An audio reference
    goes by address, which input_audio takes for files up to 25 MB.
    """
    documents: list[Json] = []
    for document in request.documents:
        if document.file_url is None:
            documents.append({'type': 'text', 'text': DOCUMENT_TEXT.format(name=document.name, text=document.text)})
        else:
            documents.append({'type': 'file', 'file': {'filename': document.name, 'file_data': document.file_url}})
    linked = {
        kind: [reference.address for reference in request.references if reference.kind == kind]
        for kind in ('image', 'video', 'audio')
    }
    images: list[Json] = [
        {'type': 'image_url', 'image_url': {'url': url}} for url in (*request.image_urls, *linked['image'])
    ]
    videos: list[Json] = [
        {'type': 'video_url', 'video_url': {'url': url}} for url in (*request.video_urls, *linked['video'])
    ]
    clips: list[Json] = [
        {'type': 'input_audio', 'input_audio': {'data': clip, 'format': WAV['FORMAT']}} for clip in request.audio_clips
    ]
    linked_clips: list[Json] = [{'type': 'input_audio', 'input_audio': {'url': url}} for url in linked['audio']]
    return [*documents, *images, *videos, *clips, *linked_clips, {'type': 'text', 'text': request.prompt}]


def _build_messages(request: ChatRequest) -> list[Json]:
    """List the system prompt, the earlier turns, then the question with its files."""
    system: list[Json] = [{'role': 'system', 'content': request.system_prompt}] if request.system_prompt.strip() else []
    turns: list[Json] = [{'role': turn.role, 'content': turn.text} for turn in request.conversation.turns]
    return [*system, *turns, {'role': 'user', 'content': _build_parts(request)}]


def build_body(request: ChatRequest, row: ModelRow) -> dict[str, Json]:
    """Add each control that the request sets, then the options of Request Options; the model row checked every control.

    max_completion_tokens caps the reasoning and the answer together, so max_tokens, which leaves the reasoning
    uncapped, is never sent. The JSON schema goes inside response_format as written. The reply is never streamed.
    """
    body: dict[str, Json] = {'model': request.model_id, 'messages': _build_messages(request)}
    if request.thinking is not None:
        body['thinking'] = {'type': request.thinking}
    if request.effort is not None:
        body['reasoning_effort'] = request.effort
    if request.max_completion_tokens > 0:
        body['max_completion_tokens'] = request.max_completion_tokens
    body.update(request.sampling)
    if request.stop:
        body['stop'] = list(request.stop)
    if request.json_schema is not None:
        body['response_format'] = {'type': 'json_schema', 'json_schema': dict(request.json_schema)}
    return build_request_body(body, request.options, 'chat', row)


__all__ = ['build_body']
