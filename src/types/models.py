"""What the bundled model table holds for one model, and how a typed ID matched it."""

from . import Kind, Value
from typing import Literal
from dataclasses import dataclass
from collections.abc import Mapping

type ModelStatus = Literal["current", "deprecated", "retiring"]
type MatchMethod = Literal["exact", "family", "listing"]


class ChatLimits(Value):
    """The chat controls one chat model takes.

    Attributes:
        context: Tokens the model holds: prompt, reasoning, and answer.
        max_input: The longest prompt, in tokens.
        max_output: The longest answer, reasoning included, in tokens: the most max_completion_tokens takes.
        max_reasoning: The longest reasoning, in tokens.
        default_max_tokens: The answer limit ModelArk applies when the request sets none.
        thinking: The thinking.type values the model takes: enabled and disabled, enabled alone when thinking cannot
            be turned off, or none.
        has_effort: Whether the model takes reasoning_effort; a model that does takes all seven values and maps some
            to others.
        default_effort: The effort the model uses when the request sets none, or None when the documents do not say.
        has_temperature: Whether temperature takes effect; False where ModelArk fixes it and ignores the value.
        answer_formats: The structured output modes: json_schema, json_object, both, or none.

    """

    context: int
    max_input: int
    max_output: int
    max_reasoning: int
    default_max_tokens: int
    thinking: tuple[str, ...]
    has_effort: bool
    default_effort: str | None
    has_temperature: bool
    answer_formats: tuple[str, ...]


class ImageLimits(Value):
    """The image controls one Seedream model takes.

    Attributes:
        size_table: Which table of pixel sizes gives the width and height of a tier and an aspect ratio.
        tiers: The size tiers the model takes.
        default_tier: The tier the model makes when the request sets no size.
        pixels: The fewest and the most pixels in all (width times height) of a WIDTHxHEIGHT size.
        max_references: The most reference images one request takes.
        has_series: Whether the model takes sequential_image_generation and max_images, so one request makes
            several images.
        backgrounds: The background values the model takes beyond its default: transparent, or none.
        output_formats: The output_format values the model takes; empty when it always makes JPEG and takes no
            format.
        prompt_modes: The optimize_prompt_options.mode values the model takes.

    """

    size_table: Literal["dola", "seedream"]
    tiers: tuple[str, ...]
    default_tier: str
    pixels: tuple[int, int]
    max_references: int
    has_series: bool
    backgrounds: tuple[str, ...]
    output_formats: tuple[str, ...]
    prompt_modes: tuple[str, ...]


class VideoLimits(Value):
    """The video controls one Seedance model takes.

    Attributes:
        modes: What a task may start from: text (a prompt alone), first_frame, first_last_frame, or references.
        resolutions: The resolution values the model takes.
        durations: The shortest and the longest duration, in seconds.
        can_choose_duration: Whether duration takes -1, which lets the model choose the length.
        adaptive_modes: The modes in which ratio must be adaptive.
        fixed_ratio_modes: The modes in which ratio may not be adaptive.
        reference_images: The most reference images one task takes; 0 when the model takes none.
        reference_videos: The most reference videos one task takes; 0 when the model takes none.
        reference_audio: The most reference audio clips one task takes; 0 when the model takes none.
        reference_seconds: The shortest and the longest reference video or audio clip, in seconds; None without
            references.
        reference_total_seconds: The most seconds of reference video, and separately of reference audio, in one
            task; None without references.
        can_use_audio_alone: Whether audio references may be the only references.
        has_audio: Whether the model takes generate_audio.
        has_seed: Whether the model takes seed (-1 to 2,147,483,647).
        has_fixed_camera: Whether the model takes camera_fixed.
        has_priority: Whether the model takes priority (0 to 9).
        output_formats: The output_format values the model takes; empty when it always makes MP4 and takes no format.
        task_types: The omni_reference_task_type values the model takes; empty when it takes none.
        draft_finishes: The resolutions a draft can be finished at; empty when the model makes no drafts.

    """

    modes: tuple[str, ...]
    resolutions: tuple[str, ...]
    durations: tuple[int, int]
    can_choose_duration: bool
    adaptive_modes: tuple[str, ...]
    fixed_ratio_modes: tuple[str, ...]
    reference_images: int
    reference_videos: int
    reference_audio: int
    reference_seconds: tuple[int, int] | None
    reference_total_seconds: int | None
    can_use_audio_alone: bool
    has_audio: bool
    has_seed: bool
    has_fixed_camera: bool
    has_priority: bool
    output_formats: tuple[str, ...]
    task_types: tuple[str, ...]
    draft_finishes: tuple[str, ...]


class EmbeddingLimits(Value):
    """The embedding controls one embedding model takes.

    Attributes:
        context: Tokens one request holds.
        dimensions: The dimensions values the model takes.
        default_dimensions: The vector length when the request sets none.

    """

    context: int
    dimensions: tuple[int, ...]
    default_dimensions: int


class MeshLimits(Value):
    """The 3D controls one 3D model takes.

    Attributes:
        dialect: Which command set the model reads, which the 3D node maps its inputs to.
        max_images: The most images in one task.
        has_inline_images: Whether images may be sent as base64 data URLs; otherwise only public addresses.
        max_prompt_characters: The longest text item; 0 when the model takes no prompt, only commands.
        textures: The texture choices the model takes.
        topologies: The topology choices the model takes.
        face_ranges: The faces allowed, by topology choice, with the model default choice for the model's default
            topology.
        precisions: The precision choices the model takes.
        has_pose: Whether the model takes a T or A pose.
        has_views: Whether the model takes image view labels.

    """

    dialect: Literal["hyper3d", "hitem3d"]
    max_images: int
    has_inline_images: bool
    max_prompt_characters: int
    textures: tuple[str, ...]
    topologies: tuple[str, ...]
    face_ranges: Mapping[str, tuple[int, int]]
    precisions: tuple[str, ...]
    has_pose: bool
    has_views: bool


class ModelRow(Value):
    """What the bundled model table holds for one model ID.

    Attributes:
        model_id: The model ID the row describes.
        kinds: The paid node kinds that take the model; layers marks a model that takes layer_decomposition.
        family: The model ID without its six-digit version, such as seed-2-0-lite or dreamina-seedance-2-0-mini.
        inputs: What the model reads: text, image, video, audio, or pdf.
        outputs: What it makes: text, image, video, embedding, or 3d.
        sources: The BytePlus pages the row was read from, as page codes such as model-list; the table index holds
            their update dates.
        has_flex: Whether the model takes service_tier flex.
        status: current; deprecated when BytePlus set a deactivation date and a newer version of the family replaces
            it; retiring when the family ends.
        deactivation: The date BytePlus stops serving the model, as YYYY-MM-DD.
        replacement: The model ID BytePlus recommends instead.

    """

    model_id: str
    kinds: frozenset[Kind]
    family: str
    inputs: frozenset[str]
    outputs: frozenset[str]
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
        kind: The kind the ID was looked up for; None for Model: Info, which takes a model of any kind.

    """

    model_id: str
    row: Row
    matched: MatchMethod
    kind: Kind | None


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
