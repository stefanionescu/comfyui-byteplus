"""Build the inputs the paid nodes share, the seed, the run number, and the options, and encode their media inputs."""

from __future__ import annotations

import torch
from comfy_api.latest import io, Input
from typing import cast, TYPE_CHECKING
from ..config.media import IMAGE_TENSOR
from ..types.images import EncodedImage
from ..config.namespace import SOCKET_TYPES
from ..types.errors import ErrorCode, ByteplusError
from ..comfy.media import encode_audio, encode_images
from ..config.generation.inputs import SEED, RUN_NUMBER, INPUT_NAMES
from ..config.messages.inputs import IMAGE_SINGLE, REFERENCE_IMAGE_SINGLE

if TYPE_CHECKING:
    from collections.abc import Sequence
    from ..types.references import Reference

# The references input every media node shares; ComfyUI only reads an input definition, so one instance serves all.
REFERENCES_INPUT = io.Custom(SOCKET_TYPES["REFERENCES"]).Input(
    "references",
    optional=True,
    tooltip=(
        "Files ModelArk reads by address: connect Reference: Add, or the references output of Image: Generate, "
        "Video: Generate, or Video: Download."
    ),
)
# The types of a socket that takes one ComfyUI image or references, passed to each such socket's MultiType input.
IMAGE_SOCKET_TYPES = (io.Image, io.Custom(SOCKET_TYPES["REFERENCES"]))


def build_request_inputs(*, has_seed: bool) -> list[io.Input]:
    """Build the seed, run number, and options inputs that follow a paid node's own inputs.

    The seed starts fixed, so queueing a workflow again never sends a new paid request by itself.
    """
    seed = io.Int.Input(
        INPUT_NAMES["SEED"],
        display_name="seed",
        tooltip="Number the model uses to vary its output. Results can change after model updates.",
        default=SEED["DEFAULT"],
        min=0,
        max=SEED["MAX"],
        control_after_generate=io.ControlAfterGenerate.fixed,
    )
    run_number = io.Int.Input(
        INPUT_NAMES["RUN_NUMBER"],
        display_name="run number",
        tooltip="Change this number to send the same request again" + (" with the same seed." if has_seed else "."),
        default=RUN_NUMBER["DEFAULT"],
        min=RUN_NUMBER["MIN"],
        max=RUN_NUMBER["MAX"],
    )
    options = io.Custom(SOCKET_TYPES["OPTIONS"]).Input(
        INPUT_NAMES["OPTIONS"],
        optional=True,
        tooltip="Connect Request Options to choose the service tier or pass extra request fields.",
    )
    return [seed, run_number, options] if has_seed else [run_number, options]


def encode_sized_images(batches: Sequence[torch.Tensor]) -> tuple[EncodedImage, ...]:
    """Encode every image of every batch, in list order and then batch order, with its size and transparency.

    A ComfyUI image is transparent only when it has a fourth channel, as Join Image with Alpha makes it.
    """
    encoded: list[EncodedImage] = []
    for batch in batches:
        urls = encode_images(batch)
        height, width, channels = batch.shape[1:]
        has_alpha = channels == IMAGE_TENSOR["RGBA_CHANNELS"]
        encoded.extend(EncodedImage(url, width, height, has_alpha) for url in urls)
    return tuple(encoded)


def encode_audio_clips(clips: Sequence[Input.Audio]) -> tuple[str, ...]:
    """Encode every clip of every batch as base64 WAV, in list order and then batch order."""
    encoded: list[str] = []
    for clip in clips:
        waveform = clip["waveform"]
        singles = (
            Input.Audio(waveform=waveform[index : index + 1], sample_rate=clip["sample_rate"])
            for index in range(waveform.shape[0])
        )
        encoded.extend(encode_audio(single) for single in singles)
    return tuple(encoded)


def read_image_socket(label: str, values: Sequence[object]) -> EncodedImage | Reference:
    """Read a socket that takes one ComfyUI image or references that hold one image.

    The socket's node takes input lists, so the values arrive as a list: images, or one references chain, whose other
    kinds this socket does not use. A tensor tells the two apart, as ComfyUI's own multi-type nodes do. More than one
    image is refused before any is encoded.
    """
    if isinstance(values[0], torch.Tensor):
        batches = cast("list[torch.Tensor]", list(values))
        if sum(batch.shape[0] for batch in batches) > 1:
            raise ByteplusError(ErrorCode.INVALID_INPUT, IMAGE_SINGLE.format(input=label))
        return encode_sized_images(batches)[0]
    chain = cast("tuple[Reference, ...]", values[0])
    images = [reference for reference in chain if reference.kind == "image"]
    if len(images) != 1:
        message = REFERENCE_IMAGE_SINGLE.format(input=label, count=len(images))
        raise ByteplusError(ErrorCode.INVALID_INPUT, message)
    return images[0]


__all__ = [
    "IMAGE_SOCKET_TYPES",
    "REFERENCES_INPUT",
    "build_request_inputs",
    "encode_audio_clips",
    "encode_sized_images",
    "read_image_socket",
]
