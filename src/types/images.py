"""Image requests, layer requests, and what ModelArk returned for them."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .options import Options
    from .references import Reference, OutputFile


@dataclass(frozen=True, slots=True)
class EncodedImage:
    """One ComfyUI image, encoded to send.

    Attributes:
        url: The image as a PNG data URL.
        width: Its width in pixels.
        height: Its height in pixels.
        has_alpha: Whether the image had a fourth channel, which the PNG keeps as transparency.

    """

    url: str
    width: int
    height: int
    has_alpha: bool


@dataclass(frozen=True, slots=True)
class ImageRequest:
    """One image request with its images already encoded; None means model default.

    Attributes:
        model_id: The model ID sent to ModelArk.
        prompt: What to draw or change.
        images: The images connected to image, in list order and then batch order.
        references: The references chain, in chain order.
        size: A size tier such as 2K, or WIDTHxHEIGHT in pixels.
        max_images: The most images to make; above 1 asks a series model for up to that many.
        background: transparent, or None.
        output_format: png or jpeg.
        prompt_mode: The optimize_prompt_options.mode, standard or fast.
        has_watermark: Whether ModelArk marks the images as AI-generated.
        options: The service tier and extra fields from Request Options.

    """

    model_id: str
    prompt: str
    images: tuple[EncodedImage, ...]
    references: tuple[Reference, ...]
    size: str | None
    max_images: int
    background: str | None
    output_format: str | None
    prompt_mode: str | None
    has_watermark: bool
    options: Options | None


@dataclass(frozen=True, slots=True)
class ImageResult:
    """Every image one request made.

    Attributes:
        outputs: The images in the order of ModelArk's reply.
        created_at: When ModelArk accepted the request, in Unix seconds.

    """

    outputs: tuple[OutputFile, ...]
    created_at: int


@dataclass(frozen=True, slots=True)
class LayerRequest:
    """One layer split request; None means model default.

    Attributes:
        model_id: The model ID sent to ModelArk.
        prompt: What to split out; empty splits every main part.
        image: The image to split: encoded here, or a reference ModelArk reads by address.
        size: The size tier of the base image and the layers.
        prompt_mode: The optimize_prompt_options.mode, standard or fast.
        has_watermark: Whether ModelArk marks the images as AI-generated.
        options: The service tier and extra fields from Request Options.

    """

    model_id: str
    prompt: str
    image: EncodedImage | Reference
    size: str
    prompt_mode: str | None
    has_watermark: bool
    options: Options | None


@dataclass(frozen=True, slots=True)
class Layer:
    """One transparent layer ModelArk split out.

    Attributes:
        content: The downloaded PNG file.
        address: The https address it was downloaded from.
        box: Where it sits on the base image: left, top, right, and bottom, in the base image's pixels.

    """

    content: bytes
    address: str
    box: tuple[int, int, int, int]


@dataclass(frozen=True, slots=True)
class LayerResult:
    """The base image and the layers of one split.

    Attributes:
        base: The base image the layers sit on.
        layers: The layers from bottom to top.
        created_at: When ModelArk accepted the request, in Unix seconds.

    """

    base: OutputFile
    layers: tuple[Layer, ...]
    created_at: int


__all__ = [
    "EncodedImage",
    "ImageRequest",
    "ImageResult",
    "Layer",
    "LayerRequest",
    "LayerResult",
]
