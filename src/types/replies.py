"""The parts of BytePlus's replies the extension reads; unknown fields are ignored."""

from . import Reply
from pydantic import Field
from typing import Literal


class ErrorBody(Reply):
    """One ModelArk error: of a failed reply, a failed task, or a failed image.

    Attributes:
        code: ModelArk's error code, whose parts are separated by dots, such as InvalidParameter.TaskTypeConstraint.
        message: ModelArk's reason.

    """

    code: str | None = None
    message: str = ""


class ErrorReply(Reply):
    """A ModelArk error document.

    Attributes:
        error: The error it describes.

    """

    error: ErrorBody


class LayerBoxReply(Reply):
    """Where one layer sits on the base image.

    Attributes:
        absolute: The left, top, right, and bottom edges, in the base image's pixels.

    """

    absolute: tuple[int, int, int, int]


class ImageItemReply(Reply):
    """One image of an image reply: a made image, a layer, or an image refused on its own.

    Attributes:
        url: The image's address, when it was made.
        z_index: A layer's place in the stack; 0 is the base image, and higher layers sit on top.
        bounding_box: Where a layer sits on the base image.
        error: Why this one image was not made, in a sequential generation that made others.

    """

    url: str | None = None
    z_index: int = 0
    bounding_box: LayerBoxReply | None = None
    error: ErrorBody | None = None


class ImageReply(Reply):
    """The image endpoint's reply.

    Attributes:
        created: When ModelArk accepted the request, in Unix seconds.
        images: Every image, under ModelArk's name data.
        error: Why no image was made, when none was.

    """

    created: int
    images: tuple[ImageItemReply, ...] = Field(default=(), alias="data")
    error: ErrorBody | None = None


class TaskCreateReply(Reply):
    """The reply to a task's create request.

    Attributes:
        id: The new task's ID.

    """

    id: str


class TaskContentReply(Reply):
    """The output addresses of a finished task.

    Attributes:
        video_url: The video.
        last_frame_url: The video's last frame, when the request asked for it.
        file_url: The 3D file.

    """

    video_url: str | None = None
    last_frame_url: str | None = None
    file_url: str | None = None


class TaskReply(Reply):
    """A video or 3D task's status check.

    Attributes:
        id: The task's ID.
        status: Where the task is: queued, running, or one of the statuses of a task that has ended.
        content: What a succeeded task made.
        error: Why a failed task failed.
        created_at: When ModelArk accepted the task, in Unix seconds.
        updated_at: When the task last changed status, in Unix seconds.

    """

    id: str
    status: Literal["queued", "running", "succeeded", "failed", "cancelled", "expired"]
    content: TaskContentReply | None = None
    error: ErrorBody | None = None
    created_at: int
    updated_at: int


class ChatMessage(Reply):
    """The assistant message of one chat choice.

    Attributes:
        content: The answer.
        reasoning_content: The model's reasoning, or a summary of it from some Seed models.

    """

    content: str | None = None
    reasoning_content: str | None = None


class ChatChoice(Reply):
    """One chat choice.

    Attributes:
        finish_reason: Why the answer ended, such as stop, length, or content_filter.
        message: The model's message.

    """

    finish_reason: str | None = None
    message: ChatMessage | None = None


class ChatReply(Reply):
    """A chat completion.

    Attributes:
        choices: The model's answers; the extension reads the first.

    """

    choices: tuple[ChatChoice, ...] = ()


class EmbeddingVector(Reply):
    """The vector of one embedding request.

    Attributes:
        embedding: The vector's values.

    """

    embedding: tuple[float, ...] = ()


class EmbeddingReply(Reply):
    """The multimodal embedding endpoint's reply: one vector for everything in the request.

    Attributes:
        vector: The vector, under ModelArk's name data.

    """

    vector: EmbeddingVector = Field(alias="data")


class ListedModalities(Reply):
    """What a listed model reads and makes.

    Attributes:
        input_modalities: What it reads, such as text, image, video, or audio.
        output_modalities: What it makes, such as text or image.

    """

    input_modalities: tuple[str, ...] = ()
    output_modalities: tuple[str, ...] = ()


class ListedStructuredOutputs(Reply):
    """The structured output modes a listed model takes.

    Attributes:
        has_json: Whether it takes json_object, which makes valid JSON without following a schema.
        has_schema: Whether it takes json_schema.

    """

    has_json: bool = Field(default=False, alias="json_object")
    has_schema: bool = Field(default=False, alias="json_schema")


class ListedFeatures(Reply):
    """What a listed model offers beyond plain text.

    Attributes:
        structured_outputs: Its structured output modes.

    """

    structured_outputs: ListedStructuredOutputs = ListedStructuredOutputs()


class ListedTokenLimits(Reply):
    """A listed model's token limits; 0 where the listing gives none.

    Attributes:
        context_window: Tokens the model holds: prompt, reasoning, and answer.
        max_output_token_length: The longest answer, reasoning included.

    """

    context_window: int = 0
    max_output_token_length: int = 0


class ListedModel(Reply):
    """One model in ModelArk's model listing.

    Attributes:
        id: The model ID.
        domain: Its kind, such as LLM, VLM, or ImageGeneration.
        status: Shutdown or Retiring; None for a current model.
        modalities: What it reads and makes.
        features: Its structured output modes.
        token_limits: Its token limits.

    """

    id: str
    domain: str = ""
    status: str | None = None
    modalities: ListedModalities = ListedModalities()
    features: ListedFeatures = ListedFeatures()
    token_limits: ListedTokenLimits = ListedTokenLimits()


class ModelListReply(Reply):
    """ModelArk's model listing: every public model, not only those the account activated.

    Attributes:
        models: Every listed model, under ModelArk's name data.

    """

    models: tuple[ListedModel, ...] = Field(default=(), alias="data")


__all__ = [
    "ChatChoice",
    "ChatMessage",
    "ChatReply",
    "EmbeddingReply",
    "EmbeddingVector",
    "ErrorBody",
    "ErrorReply",
    "ImageItemReply",
    "ImageReply",
    "LayerBoxReply",
    "ListedFeatures",
    "ListedModalities",
    "ListedModel",
    "ListedStructuredOutputs",
    "ListedTokenLimits",
    "ModelListReply",
    "TaskContentReply",
    "TaskCreateReply",
    "TaskReply",
]
