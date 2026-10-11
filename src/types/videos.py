"""Video requests."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .options import Options
    from .images import EncodedImage
    from .references import Reference


@dataclass(frozen=True, slots=True)
class VideoRequest:
    """One Seedance request with its local media already encoded; None means model default.

    Attributes:
        model_id: The model ID sent to ModelArk.
        prompt: What the video shows; empty to finish a draft.
        duration: The length in seconds; -1 lets the model choose.
        resolution: The resolution to send; a draft is made at 480p instead.
        ratio: The aspect ratio, or adaptive.
        has_audio: The generate_audio value: whether the video has sound.
        omni_reference_task_type: auto, reference, edit, or extend; auto sends nothing.
        is_draft: Whether to make a 480p draft.
        is_camera_fixed: Whether to ask the model to keep the camera still.
        output_format: mp4 or mov.
        has_watermark: Whether ModelArk marks the video as AI-generated.
        first_frame: The image the video starts from: encoded here, or a reference ModelArk reads by address.
        last_frame: The image the video ends on, in the same forms.
        images: The images connected to reference_image, in list order and then batch order.
        clips: The clips connected to reference_audio as base64 WAV, in list order and then batch order.
        references: The references chain, in chain order.
        seed: The seed, sent only to models that take one.
        options: The service tier and extra fields from Request Options.

    """

    model_id: str
    prompt: str
    duration: int
    resolution: str
    ratio: str | None
    has_audio: bool | None
    omni_reference_task_type: str
    is_draft: bool
    is_camera_fixed: bool
    output_format: str | None
    has_watermark: bool
    first_frame: EncodedImage | Reference | None
    last_frame: EncodedImage | Reference | None
    images: tuple[EncodedImage, ...]
    clips: tuple[str, ...]
    references: tuple[Reference, ...]
    seed: int
    options: Options | None


__all__ = ["VideoRequest"]
