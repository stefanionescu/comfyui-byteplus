"""What the bundled model table holds for one model, and how a typed ID matched it."""

from . import Kind, Value
from typing import Literal
from dataclasses import dataclass

type ModelStatus = Literal["current", "deprecated", "retiring"]
type SamplingMode = Literal["always", "with_thinking", "without_thinking"]
type MatchMethod = Literal["exact", "family", "listing"]


class ChatLimits(Value):
    """The chat controls one chat model takes.

    Attributes:
        context: Tokens the model holds: prompt, reasoning, and answer.
        max_output: The longest answer, reasoning included, in tokens.
        thinking: The thinking.type values the model takes: enabled and disabled, enabled alone when thinking cannot
            be turned off, or none.
        has_effort: Whether the model takes reasoning_effort; a model that does takes all seven values and maps some
            to others.
        sampling: The sampling fields that take effect, each always, only with thinking, or only without it. ModelArk
            fixes every other field and ignores its value.
        max_stop: The most stop words the model takes; 0 when it ignores stop.
        response_formats: The structured output modes: json_schema, json_object, both, or none.

    """

    context: int
    max_output: int
    thinking: tuple[str, ...]
    has_effort: bool
    sampling: dict[str, SamplingMode]
    max_stop: int
    response_formats: tuple[str, ...]


class ImageLimits(Value):
    """The image controls one Seedream model takes.

    Attributes:
        sizes: The sizes the model takes by name, such as 2K; it takes any WIDTHxHEIGHT besides.
        has_sequential_image_generation: Whether the model takes sequential_image_generation and max_images, so one
            request makes several images.
        backgrounds: The background values the model takes beyond its default: transparent, or none.
        output_formats: The output_format values the model takes; empty when it always makes JPEG and takes no
            format.
        optimize_prompt_modes: The optimize_prompt_options.mode values the model takes.

    """

    sizes: tuple[str, ...]
    has_sequential_image_generation: bool
    backgrounds: tuple[str, ...]
    output_formats: tuple[str, ...]
    optimize_prompt_modes: tuple[str, ...]


class VideoLimits(Value):
    """The video controls one Seedance model takes.

    Attributes:
        modes: What a task can start from: text (a prompt alone), first_frame, first_last_frame, or references.
        resolutions: The resolution values the model takes.
        durations: The shortest and the longest duration, in seconds.
        can_choose_duration: Whether duration takes -1, which lets the model choose the length.
        adaptive_modes: The modes in which ratio must be adaptive.
        fixed_ratio_modes: The modes in which ratio cannot be adaptive.
        has_audio: Whether the model takes generate_audio.
        has_seed: Whether the model takes seed (-1 to 2,147,483,647).
        has_fixed_camera: Whether the model takes camera_fixed.
        output_formats: The output_format values the model takes; empty when it always makes MP4 and takes no format.
        omni_reference_task_types: The omni_reference_task_type values the model takes; empty when it takes none.
        draft_resolutions: The resolutions a draft can be finished at; empty when the model makes no drafts.

    """

    modes: tuple[str, ...]
    resolutions: tuple[str, ...]
    durations: tuple[int, int]
    can_choose_duration: bool
    adaptive_modes: tuple[str, ...]
    fixed_ratio_modes: tuple[str, ...]
    has_audio: bool
    has_seed: bool
    has_fixed_camera: bool
    output_formats: tuple[str, ...]
    omni_reference_task_types: tuple[str, ...]
    draft_resolutions: tuple[str, ...]


class EmbeddingLimits(Value):
    """The embedding controls one embedding model takes.

    Attributes:
        context: Tokens one request holds.
        dimensions: The dimensions values the model takes.

    """

    context: int
    dimensions: tuple[int, ...]


class MeshLimits(Value):
    """The 3D controls one 3D model takes.

    Attributes:
        format_command: The command that asks for a GLB file, as the model's page writes it; the 3D node adds it, since
            Hitem3D makes OBJ without it.
        max_prompt_characters: The longest text item, commands included; 0 when the model's page names no limit.

    """

    format_command: str
    max_prompt_characters: int


class ModelRow(Value):
    """What the bundled model table holds for one model ID.

    Attributes:
        model_id: The model ID the row describes.
        kinds: The paid node kinds that take the model; layers marks a model that takes layer_decomposition.
        inputs: What the model reads: text, image, video, audio, or pdf.
        sources: The BytePlus pages the row was read from, as page codes such as model-list; SOURCE_DATES holds
            their update dates.
        has_flex: Whether the model takes service_tier flex.
        status: current; deprecated when BytePlus set a deactivation date and a newer version of the family replaces
            it; retiring when the family ends.
        deactivation: The date BytePlus stops serving the model, as YYYY-MM-DD.
        replacement: The model ID BytePlus recommends instead.

    """

    model_id: str
    kinds: frozenset[Kind]
    inputs: frozenset[str]
    sources: tuple[str, ...]
    has_flex: bool = False
    status: ModelStatus = "current"
    deactivation: str | None = None
    replacement: str | None = None


class ChatRow(ModelRow):
    """The row of a chat model.

    Attributes:
        chat: The chat controls the model takes.

    """

    chat: ChatLimits


class ImageRow(ModelRow):
    """The row of a Seedream model, whether it makes images, splits layers, or both.

    Attributes:
        image: The image controls the model takes.

    """

    image: ImageLimits


class VideoRow(ModelRow):
    """The row of a Seedance model.

    Attributes:
        video: The video controls the model takes.

    """

    video: VideoLimits


class EmbeddingRow(ModelRow):
    """The row of an embedding model.

    Attributes:
        embedding: The embedding controls the model takes.

    """

    embedding: EmbeddingLimits


class MeshRow(ModelRow):
    """The row of a 3D model.

    Attributes:
        mesh: The 3D controls the model takes.

    """

    mesh: MeshLimits


@dataclass(frozen=True, slots=True)
class ModelMatch[Row: ModelRow]:
    """How a typed model ID matched a row of the bundled table, or of ModelArk's model listing.

    Attributes:
        model_id: The typed ID without surrounding whitespace: the ID every request sends.
        row: The row the checks use.
        matched: exact when the ID names a row or an alias; family for another version of a known family; listing
            for a chat model the table lacks, read from ModelArk's model listing.

    """

    model_id: str
    row: Row
    matched: MatchMethod


__all__ = [
    "ChatLimits",
    "ChatRow",
    "EmbeddingLimits",
    "EmbeddingRow",
    "ImageLimits",
    "ImageRow",
    "MeshLimits",
    "MeshRow",
    "ModelMatch",
    "ModelRow",
    "VideoLimits",
    "VideoRow",
]
