"""Split one image into a base image and transparent layers with Seedream 5.0 pro or flash."""

from __future__ import annotations

import torch
import asyncio
from ..base import PaidNode
from comfy_api.latest import io
from typing import TYPE_CHECKING
from ...comfy.media import decode_image
from ...types.images import LayerRequest
from torch.nn.functional import pad, interpolate
from ...config.namespace import MENUS, NODE_PREFIX
from comfy_execution.graph import ExecutionBlocker
from ...byteplus.images.layers import LayerOperation
from ...config.generation.models import DEFAULT_MODELS
from ...config.generation.images import LAYER_SIZES, LAYER_SIZE_DEFAULT
from ...comfy.execution import send_request, wait_for_task, wait_for_thread
from ...config.generation.inputs import INPUT_NAMES, MODEL_DEFAULT, MODEL_TOOLTIP
from ..inputs import (
    WATERMARK_INPUT,
    read_image_socket,
    IMAGE_SOCKET_TYPES,
    build_request_inputs,
    OPTIMIZE_PROMPT_OPTIONS_INPUT,
)

if TYPE_CHECKING:
    from ...types.options import Options
    from ...types.images import LayerResult


def _build_scaled_layer(
    pixels: torch.Tensor, mask: torch.Tensor, size: tuple[int, int]
) -> tuple[torch.Tensor, torch.Tensor]:
    """Scale a layer and its mask to a height and width with bilinear filtering and antialiasing.

    The color is scaled premultiplied, color times alpha, and then divided by the scaled alpha, so the layer's
    transparent edges keep no dark fringe. Where the scaled alpha is 0, the color is black.
    """
    alpha = (1.0 - mask).unsqueeze(-1)
    premultiplied = torch.cat((pixels * alpha, alpha), dim=-1).movedim(-1, 1)
    scaled = interpolate(premultiplied, size=size, mode="bilinear", antialias=True, align_corners=False).movedim(1, -1)
    scaled_alpha = scaled[..., 3:].clamp(0.0, 1.0)
    color = (scaled[..., :3] / scaled_alpha.clamp(min=torch.finfo(scaled.dtype).tiny)).clamp(0.0, 1.0)
    return color, 1.0 - scaled_alpha.squeeze(-1)


def _place_layer(
    pixels: torch.Tensor, mask: torch.Tensor, box: tuple[int, int, int, int], canvas: tuple[int, int]
) -> tuple[torch.Tensor, torch.Tensor]:
    """Place one layer at its box on a canvas the size of the base image, black and masked outside the layer.

    ModelArk's layer can differ in size from its box, so it is scaled to the box first. A mask is 1 minus alpha, so
    the canvas outside the layer is white in the mask.
    """
    left, top, right, bottom = box
    width, height = canvas
    box_size = (bottom - top, right - left)
    if pixels.shape[1:3] != box_size:
        pixels, mask = _build_scaled_layer(pixels, mask, box_size)
    # Padding moves the layer to its box; a negative margin crops any part of the box beyond the canvas.
    margins = (left, width - right, top, height - bottom)
    return pad(pixels, (0, 0, *margins)), pad(mask, margins, value=1.0)


def _build_outputs(result: LayerResult) -> io.NodeOutput:
    """Decode the base image, and place each layer and its mask on a canvas the base image's size."""
    base, _mask = decode_image(result.base)
    canvas = (base.shape[2], base.shape[1])
    placed = [_place_layer(*decode_image(layer.content), layer.box, canvas) for layer in result.layers]
    return io.NodeOutput(
        base,
        [pixels for pixels, _mask in placed] or ExecutionBlocker(None),
        [mask for _pixels, mask in placed] or ExecutionBlocker(None),
    )


class ImageSplitLayers(PaidNode):
    """Send one layer split and return the base image and each layer with its mask.

    The node takes input lists, so a connected list reaches it whole and is refused, instead of running one paid
    request per image.
    """

    list_inputs = frozenset({"image"})

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the model, the split controls, the image socket, and the prompt."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Image: Split Layers",
            category=MENUS["IMAGE"],
            description="Split an image into a base image and transparent layers.",
            inputs=[
                io.String.Input(INPUT_NAMES["MODEL"], default=DEFAULT_MODELS["layers"], tooltip=MODEL_TOOLTIP),
                io.Combo.Input(
                    "size",
                    options=list(LAYER_SIZES),
                    default=LAYER_SIZE_DEFAULT,
                    tooltip=(
                        "The size of the base image and layers. With auto, it keeps the input image's size, within "
                        "1K to 2K."
                    ),
                ),
                OPTIMIZE_PROMPT_OPTIONS_INPUT,
                WATERMARK_INPUT,
                io.MultiType.Input(
                    "image",
                    types=list(IMAGE_SOCKET_TYPES),
                    tooltip="The image to split: one image, or references that hold one image.",
                ),
                *build_request_inputs(),
                io.String.Input(
                    "prompt",
                    multiline=True,
                    default="",
                    tooltip=(
                        "What to split out. Leave it empty to split every main part. Mark a region with "
                        "<bbox>left top right bottom</bbox>, each from 0 to 999."
                    ),
                ),
            ],
            outputs=[
                io.Image.Output("base", display_name="base"),
                io.Image.Output("layers", display_name="layers", is_output_list=True),
                io.Mask.Output("masks", display_name="masks", is_output_list=True),
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
        image: list[object],
        size: str,
        optimize_prompt_options: str,
        watermark: bool,
        options: Options | None = None,
    ) -> io.NodeOutput:
        """Wait for the split in an owned task, so ComfyUI's cancel reaches the encoding and the request."""

        async def send_encoded() -> io.NodeOutput:
            """Read the image socket in a worker thread, then send the split."""
            source = await wait_for_thread(lambda: read_image_socket("image", image))
            request = LayerRequest(
                model_id=model.strip(),
                prompt=prompt,
                image=source,
                size=size,
                optimize_prompt_mode=None if optimize_prompt_options == MODEL_DEFAULT else optimize_prompt_options,
                has_watermark=watermark,
                options=options,
            )
            return await send_request(LayerOperation(request), _build_outputs, cls.hidden.unique_id)

        return await wait_for_task(asyncio.create_task(send_encoded()))


__all__ = ["ImageSplitLayers"]
