"""Ask any ModelArk chat model, with images, video, audio, or documents when the model reads them."""

from __future__ import annotations

import asyncio
from ..base import PaidNode
from comfy_api.latest import io
from typing import cast, TYPE_CHECKING
from ...comfy.media import encode_video
from ...types.parsing import parse_fields
from comfy_execution.graph import ExecutionBlocker
from ...byteplus.chat.operation import ChatOperation
from ...config.generation.models import DEFAULT_MODELS
from ...config.messages.inputs import JSON_SCHEMA_INVALID
from ...types.chat import Turn, ChatRequest, Conversation
from ...config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES
from ...comfy.execution import send_request, wait_for_task, wait_for_thread
from ...config.generation.inputs import INPUT_NAMES, MODEL_DEFAULT, MODEL_TOOLTIP
from ..inputs import REFERENCES_INPUT, encode_audio_clips, encode_sized_images, build_request_inputs
from ...config.generation.chat import EFFORTS, TEMPERATURE, THINKING_CHOICES, TEMPERATURE_CHOICE, MAX_COMPLETION_TOKENS

if TYPE_CHECKING:
    import torch
    from comfy_api.latest import Input
    from collections.abc import Mapping
    from ...types.options import Options
    from ...types.references import Reference
    from ...types.chat import Document, ChatResult


# One socket for each kind of media; everything connected goes in one request, each item at its own size.
_MEDIA = (
    io.Image.Input(
        "images",
        optional=True,
        tooltip="Images for the model to read: one, a batch, or a list. Create List joins several Load Image nodes.",
    ),
    io.Video.Input("videos", optional=True, tooltip="Videos for the model to read. Create List joins several."),
    io.Audio.Input(
        "audio",
        optional=True,
        tooltip="Audio clips for models that read audio, such as seed-2-0-lite-260428. Create List joins several.",
    ),
)


# The controls a chat model may take; each left at its default sends nothing.
_CONTROLS = (
    io.Combo.Input(
        "thinking",
        options=list(THINKING_CHOICES),
        default=MODEL_DEFAULT,
        tooltip=(
            "Whether the model reasons before answering. It answers faster and costs less when disabled; some "
            "models always think."
        ),
    ),
    io.Combo.Input(
        "reasoning_effort",
        options=list(EFFORTS),
        default=MODEL_DEFAULT,
        advanced=True,
        tooltip="How much the model reasons before answering. With thinking set to disabled, only minimal is allowed.",
    ),
    io.Int.Input(
        "max_completion_tokens",
        default=0,
        min=0,
        max=MAX_COMPLETION_TOKENS,
        advanced=True,
        tooltip=(
            "The most tokens the model may write, reasoning included; 0 keeps the model's own limit, 4,096 tokens on "
            "most models."
        ),
    ),
    io.DynamicCombo.Input(
        TEMPERATURE_CHOICE["INPUT"],
        options=[
            io.DynamicCombo.Option(MODEL_DEFAULT, []),
            io.DynamicCombo.Option(
                TEMPERATURE_CHOICE["SET"],
                [
                    io.Float.Input(
                        TEMPERATURE_CHOICE["VALUE"],
                        default=TEMPERATURE["DEFAULT"],
                        min=0,
                        max=TEMPERATURE["MAX"],
                        step=TEMPERATURE["STEP"],
                        advanced=True,
                        tooltip="Higher values vary the answer more.",
                    )
                ],
            ),
        ],
        tooltip="How much the answer varies. Choose set to send a value to models that take a temperature.",
        extra_dict={"advanced": True},
    ),
)


def _read_temperature(choice: Mapping[str, object] | None) -> float | None:
    """Read the set temperature; model default, or no choice from a node that calls this one, sends none."""
    if choice is None or choice[TEMPERATURE_CHOICE["INPUT"]] != TEMPERATURE_CHOICE["SET"]:
        return None
    return float(cast("float", choice[TEMPERATURE_CHOICE["VALUE"]]))


def _build_outputs(result: ChatResult, history: Conversation, prompt: str) -> io.NodeOutput:
    """Return the answer and the reasoning, and extend the conversation with this exchange's words."""
    turns = (*history.turns, Turn("user", prompt), Turn("assistant", result.text))
    reasoning: object = result.reasoning or ExecutionBlocker(None)
    return io.NodeOutput(result.text, reasoning, Conversation(turns))


class ChatAsk(PaidNode):
    """Send one chat completion and return the answer, the reasoning, and the conversation."""

    list_inputs = frozenset({"images", "videos", "audio"})

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the model, the conversation, the media sockets, every control a chat model may take, and the text."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Chat: Ask",
            category=MENUS["CHAT"],
            description=(
                "Ask any ModelArk chat model, with images, video, audio, or documents when the model reads them."
            ),
            inputs=[
                io.String.Input(INPUT_NAMES["MODEL"], default=DEFAULT_MODELS["chat"], tooltip=MODEL_TOOLTIP),
                io.Custom(SOCKET_TYPES["CONVERSATION"]).Input(
                    "conversation", optional=True, tooltip="Connect a previous Chat: Ask to continue its conversation."
                ),
                io.Custom(SOCKET_TYPES["DOCUMENTS"]).Input(
                    "documents",
                    optional=True,
                    tooltip=(
                        "Connect Chat: Attach Document. PDFs need a model that reads them; text files go to any model."
                    ),
                ),
                *_MEDIA,
                REFERENCES_INPUT,
                *_CONTROLS,
                *build_request_inputs(),
                io.String.Input(
                    "json_schema",
                    default="",
                    multiline=True,
                    advanced=True,
                    tooltip=(
                        "Sent as response_format.json_schema: a JSON object with a name and a schema. Leave it empty "
                        "for free text."
                    ),
                ),
                io.String.Input("prompt", multiline=True, default="", tooltip="The question or instruction."),
                io.String.Input(
                    "system_prompt",
                    multiline=True,
                    default="",
                    optional=True,
                    advanced=True,
                    tooltip="Instructions the model follows for the whole answer.",
                ),
            ],
            outputs=[
                io.String.Output("text", display_name="text"),
                io.String.Output("reasoning", display_name="reasoning"),
                io.Custom(SOCKET_TYPES["CONVERSATION"]).Output("conversation", display_name="conversation"),
            ],
            is_input_list=True,
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    async def send(  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        prompt: str,
        model: str,
        thinking: str = MODEL_DEFAULT,
        reasoning_effort: str = MODEL_DEFAULT,
        max_completion_tokens: int = 0,
        temperature: Mapping[str, object] | None = None,
        json_schema: str = "",
        system_prompt: str = "",
        conversation: Conversation | None = None,
        documents: tuple[Document, ...] | None = None,
        images: list[torch.Tensor] | None = None,
        videos: list[Input.Video] | None = None,
        audio: list[Input.Audio] | None = None,
        references: tuple[Reference, ...] | None = None,
        options: Options | None = None,
    ) -> io.NodeOutput:
        """Read the schema before any media is encoded, then wait for the request in an owned task."""
        history = conversation or Conversation(())
        schema = parse_fields(json_schema, JSON_SCHEMA_INVALID)
        temperature_value = _read_temperature(temperature)

        async def send_encoded() -> io.NodeOutput:
            """Encode the media in a worker thread, then send the request."""
            image_urls, video_urls, clips = await wait_for_thread(
                lambda: (
                    tuple(image.url for image in encode_sized_images(images or ())),
                    tuple(encode_video(video) for video in videos or ()),
                    encode_audio_clips(audio or ()),
                )
            )
            request = ChatRequest(
                model_id=model.strip(),
                system_prompt=system_prompt,
                prompt=prompt,
                conversation=history,
                image_urls=image_urls,
                video_urls=video_urls,
                audio_clips=clips,
                documents=documents or (),
                references=references or (),
                thinking=None if thinking == MODEL_DEFAULT else thinking,
                effort=None if reasoning_effort == MODEL_DEFAULT else reasoning_effort,
                max_completion_tokens=max_completion_tokens,
                temperature=temperature_value,
                json_schema=schema,
                options=options,
            )
            return await send_request(
                ChatOperation(request), lambda result: _build_outputs(result, history, prompt), cls.hidden.unique_id
            )

        return await wait_for_task(asyncio.create_task(send_encoded()))


__all__ = ["ChatAsk"]
