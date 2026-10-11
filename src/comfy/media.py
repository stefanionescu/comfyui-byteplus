"""Check ComfyUI media, then convert it with ComfyUI's own helpers to what ModelArk reads and from what BytePlus sends.

Encoding and decoding block, so callers run these functions through wait_for_thread.
"""

from __future__ import annotations

import io
import torch
from typing import TYPE_CHECKING
from comfy_api.latest import Types
from ..types.errors import ErrorCode, ByteplusError
from ..config.media import WAV, IMAGE_TENSOR, MP4_URL_PREFIX, MAX_IMAGE_PIXELS
from ..config.messages.media import (
    AUDIO_EMPTY,
    IMAGE_SHAPE,
    IMAGE_PIXELS,
    IMAGE_TOO_LARGE,
    AUDIO_UNWRITABLE,
    IMAGE_UNREADABLE,
    VIDEO_UNWRITABLE,
)
from comfy_api_nodes.util.conversions import (
    tensor_to_data_uri,
    audio_to_base64_string,
    video_to_base64_string,
    bytesio_to_image_tensor,
)

if TYPE_CHECKING:
    from comfy_api.latest import Input


def encode_images(image: torch.Tensor) -> tuple[str, ...]:
    """Encode every image of a batch as a PNG data URL, never shrinking it; an image ModelArk cannot read is refused.

    Every frame of a batch has the same size, so one pixel count covers the batch.
    """
    if image.ndim != IMAGE_TENSOR["DIMENSIONS"] or image.shape[-1] not in {
        IMAGE_TENSOR["RGB_CHANNELS"],
        IMAGE_TENSOR["RGBA_CHANNELS"],
    }:
        raise ByteplusError(ErrorCode.INVALID_INPUT, IMAGE_SHAPE)
    if not bool(torch.isfinite(image).all()):
        raise ByteplusError(ErrorCode.INVALID_INPUT, IMAGE_PIXELS)
    height, width = image.shape[1], image.shape[2]
    if height * width > MAX_IMAGE_PIXELS:
        message = IMAGE_TOO_LARGE.format(width=width, height=height, maximum=f"{MAX_IMAGE_PIXELS:,}")
        raise ByteplusError(ErrorCode.INVALID_INPUT, message)
    try:
        return tuple(tensor_to_data_uri(frame.clamp(0, 1), total_pixels=None) for frame in image)
    except Exception:  # noqa: BLE001 -- reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise ByteplusError(ErrorCode.MEDIA, IMAGE_SHAPE) from None


def decode_image(content: bytes) -> tuple[torch.Tensor, torch.Tensor]:
    """Read one image as pixels [1, H, W, 3] and its mask [1, H, W], where the mask is 1 minus alpha."""
    try:
        pixels = bytesio_to_image_tensor(io.BytesIO(content))
    except Exception:  # noqa: BLE001 -- reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise ByteplusError(ErrorCode.MEDIA, IMAGE_UNREADABLE) from None
    if pixels.shape[-1] == IMAGE_TENSOR["RGBA_CHANNELS"]:
        return pixels[..., : IMAGE_TENSOR["RGB_CHANNELS"]].contiguous(), 1.0 - pixels[..., IMAGE_TENSOR["RGB_CHANNELS"]]
    return pixels, torch.zeros(pixels.shape[:3], dtype=pixels.dtype)


def encode_audio(audio: Input.Audio) -> str:
    """Encode one audio clip as base64 WAV, without a data: prefix."""
    if audio["waveform"].shape[-1] == 0:
        raise ByteplusError(ErrorCode.INVALID_INPUT, AUDIO_EMPTY)
    try:
        return audio_to_base64_string(audio, container_format=WAV["FORMAT"], codec_name=WAV["CODEC"])
    except Exception:  # noqa: BLE001 -- reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise ByteplusError(ErrorCode.MEDIA, AUDIO_UNWRITABLE) from None


def encode_video(video: Input.Video) -> str:
    """Encode a ComfyUI video as an H.264 MP4 data URL."""
    try:
        return MP4_URL_PREFIX + video_to_base64_string(video, Types.VideoContainer.MP4, Types.VideoCodec.H264)
    except Exception:  # noqa: BLE001 -- reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise ByteplusError(ErrorCode.MEDIA, VIDEO_UNWRITABLE) from None


__all__ = ["decode_image", "encode_audio", "encode_images", "encode_video"]
