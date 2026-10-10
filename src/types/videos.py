"""Video requests and the audio clips they carry."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .options import Options
    from .images import EncodedImage
    from .references import Reference


@dataclass(frozen=True, slots=True)
class EncodedAudio:
    """One ComfyUI audio clip, encoded to send.

    Attributes:
        url: The clip as a WAV data URL.
        seconds: Its length.

    """

    url: str
    seconds: float


@dataclass(frozen=True, slots=True)
class VideoRequest:
    """One Seedance request with its local media already encoded; None means model default.

    Attributes:
        model_id: The model ID sent to ModelArk.
        prompt: What the video shows; empty to finish a draft.
        duration: The length in seconds; 0 lets the model choose.
        resolution: The resolution, always sent except to finish a draft.
        aspect_ratio: The aspect ratio.
        has_sound: Whether the video has sound.
        task_type: auto, reference, edit, or extend; auto sends nothing.
        is_draft: Whether to make a 480p draft.
        is_camera_fixed: Whether to ask the model to keep the camera still.
        output_format: mp4 or mov.
        has_watermark: Whether ModelArk marks the video as AI-generated.
        first_frame: The image the video starts from: encoded here, or a reference ModelArk reads by address.
        last_frame: The image the video ends on, in the same forms.
        images: The images connected to reference images, in list order and then batch order.
        clips: The clips connected to reference audio, in list order and then batch order.
        references: The references chain, in chain order.
        seed: The seed, sent only to models that take one.
        options: The service tier and extra fields from Request Options.

    """

    model_id: str
    prompt: str
    duration: int
    resolution: str
    aspect_ratio: str | None
    has_sound: bool | None
    task_type: str
    is_draft: bool
    is_camera_fixed: bool
    output_format: str | None
    has_watermark: bool
    first_frame: EncodedImage | Reference | None
    last_frame: EncodedImage | Reference | None
    images: tuple[EncodedImage, ...]
    clips: tuple[EncodedAudio, ...]
    references: tuple[Reference, ...]
    seed: int
    options: Options | None


__all__ = ["EncodedAudio", "VideoRequest"]
