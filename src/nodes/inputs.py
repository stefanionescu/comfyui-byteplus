"""Build the inputs and outputs the nodes share, and encode their media inputs."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import torch
from comfy_api.latest import Input, io

from ..comfy.media import encode_audio, encode_images
from ..config.media import IMAGE_TENSOR
from ..state.errors import ErrorCode, BytePlusError
from ..state.images import EncodedImage
from ..config.namespace import SOCKET_TYPES
from ..config.messages.inputs import IMAGE_SINGLE, REFERENCE_IMAGE_SINGLE
from ..config.generation.images import OPTIMIZE_PROMPT_MODES
from ..config.generation.inputs import RUN_NUMBER, INPUT_NAMES, MODEL_DEFAULT

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ..state.references import Reference

# The references input of every node that takes references; ComfyUI only reads an input definition, so one serves all.
REFERENCES_INPUT = io.Custom(SOCKET_TYPES['REFERENCES']).Input(
    'references',
    optional=True,
    tooltip=(
        'Files ModelArk reads by address: connect Reference: Add, or the references output of Image: Generate, '
        'Video: Generate, or Video: Download.'
    ),
)
# The references output of every node that returns references; ComfyUI only reads an output definition, so one serves
# all.
REFERENCES_OUTPUT = io.Custom(SOCKET_TYPES['REFERENCES']).Output('references', display_name='references')
# The optimize_prompt_options input of the Seedream nodes.
OPTIMIZE_PROMPT_OPTIONS_INPUT = io.Combo.Input(
    'optimize_prompt_options',
    options=list(OPTIMIZE_PROMPT_MODES),
    default=MODEL_DEFAULT,
    advanced=True,
    tooltip='With fast, images come sooner at slightly lower quality, on models that offer it.',
)
# The watermark input of the image and video nodes.
WATERMARK_INPUT = io.Boolean.Input(
    'watermark',
    default=False,
    advanced=True,
    tooltip='Adds an AI-generated mark in the lower right corner.',
)
# The types of a socket that takes one ComfyUI image or references, passed to each such socket's MultiType input.
IMAGE_SOCKET_TYPES = (io.Image, io.Custom(SOCKET_TYPES['REFERENCES']))


def build_request_inputs() -> list[io.Input]:
    """Build the run number and options inputs that come after the other inputs of a paid node."""
    run_number = io.Int.Input(
        INPUT_NAMES['RUN_NUMBER'],
        tooltip='Change this number to send the same request again.',
        default=RUN_NUMBER['DEFAULT'],
        min=RUN_NUMBER['MIN'],
        max=RUN_NUMBER['MAX'],
    )
    options = io.Custom(SOCKET_TYPES['OPTIONS']).Input(
        INPUT_NAMES['OPTIONS'],
        optional=True,
        tooltip='Connect Request Options to choose service_tier or add extra_fields.',
    )
    return [run_number, options]


def encode_sized_images(batches: Sequence[torch.Tensor]) -> tuple[EncodedImage, ...]:
    """Encode every image of every batch with its size and transparency, in list order, then batch order.

    A ComfyUI image is transparent only when it has a fourth channel, as Join Image with Alpha makes it.
    """
    encoded: list[EncodedImage] = []
    for batch in batches:
        urls = encode_images(batch)
        height, width, channels = batch.shape[1:]
        has_alpha = channels == IMAGE_TENSOR['RGBA_CHANNELS']
        encoded.extend(EncodedImage(url, width, height, has_alpha) for url in urls)
    return tuple(encoded)


def encode_audio_clips(clips: Sequence[Input.Audio]) -> tuple[str, ...]:
    """Encode every clip of every batch as base64 WAV, in list order, then batch order."""
    encoded: list[str] = []
    for clip in clips:
        waveform = clip['waveform']
        singles = (
            Input.Audio(waveform=waveform[index : index + 1], sample_rate=clip['sample_rate'])
            for index in range(waveform.shape[0])
        )
        encoded.extend(encode_audio(single) for single in singles)
    return tuple(encoded)


def read_image_socket(label: str, values: Sequence[object]) -> EncodedImage | Reference:
    """Read a socket that takes one ComfyUI image or references that hold one image.

    The socket's node takes input lists, so the values arrive as a list: images, or one references chain, whose other
    kinds this socket does not use. A tensor separates the two, as in the multi-type nodes that ComfyUI ships. The
    function refuses more than one image before it encodes any.
    """
    if isinstance(values[0], torch.Tensor):
        batches = cast('list[torch.Tensor]', list(values))
        if sum(batch.shape[0] for batch in batches) > 1:
            raise BytePlusError(ErrorCode.INVALID_INPUT, IMAGE_SINGLE.format(input=label))
        return encode_sized_images(batches)[0]
    chain = cast('tuple[Reference, ...]', values[0])
    images = [reference for reference in chain if reference.kind == 'image']
    if len(images) != 1:
        message = REFERENCE_IMAGE_SINGLE.format(input=label, count=len(images))
        raise BytePlusError(ErrorCode.INVALID_INPUT, message)
    return images[0]


__all__ = [
    'IMAGE_SOCKET_TYPES',
    'OPTIMIZE_PROMPT_OPTIONS_INPUT',
    'REFERENCES_INPUT',
    'REFERENCES_OUTPUT',
    'WATERMARK_INPUT',
    'build_request_inputs',
    'encode_audio_clips',
    'encode_sized_images',
    'read_image_socket',
]
