"""Generate or edit images with any Seedream model, and keep each image's ModelArk address as a reference."""

from __future__ import annotations

import asyncio
from ..base import PaidNode
from comfy_api.latest import io
from typing import TYPE_CHECKING
from ...comfy.media import decode_image
from ...types.images import ImageRequest
from ...byteplus.images.generate import ImageOperation
from ...config.generation.models import DEFAULT_MODELS
from ...byteplus.references import build_output_reference
from ...config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES
from ...comfy.execution import send_request, wait_for_task, wait_for_thread
from ...config.generation.images import MAX_IMAGES, BACKGROUNDS, OUTPUT_FORMATS
from ...config.generation.inputs import INPUT_NAMES, MODEL_DEFAULT, MODEL_TOOLTIP
from ..inputs import (
    WATERMARK_INPUT,
    REFERENCES_INPUT,
    encode_sized_images,
    build_request_inputs,
    OPTIMIZE_PROMPT_OPTIONS_INPUT,
)

if TYPE_CHECKING:
    import torch
    from ...types.options import Options
    from ...types.images import ImageResult
    from ...types.references import Reference

# The image controls; an empty size and a dropdown left at default send nothing.
_CONTROLS = (
    io.String.Input(
        "size",
        default="",
        tooltip=(
            "A size such as 2K, or pixels such as 2048x1152; empty leaves it to the model. Model: Info lists the sizes."
        ),
    ),
    io.Int.Input(
        "max_images",
        default=MAX_IMAGES["DEFAULT"],
        min=1,
        max=MAX_IMAGES["MAX"],
        tooltip=(
            "The most images to make. Above 1, only models with sequential image generation take it, and the prompt "
            'must ask for that many, such as "Generate 4 images of a lighthouse".'
        ),
    ),
    io.Combo.Input(
        "background",
        options=list(BACKGROUNDS),
        default=MODEL_DEFAULT,
        tooltip="With transparent, the node keeps the transparency of one reference image that has it, and makes "
        "a PNG.",
    ),
    io.Combo.Input(
        "output_format",
        options=list(OUTPUT_FORMATS),
        default=MODEL_DEFAULT,
        tooltip="PNG or JPEG. With default, the model makes JPEG.",
    ),
    OPTIMIZE_PROMPT_OPTIONS_INPUT,
    WATERMARK_INPUT,
)


def _build_outputs(result: ImageResult) -> io.NodeOutput:
    """Decode each image with its mask, and keep each image's address as an image reference."""
    decoded = [decode_image(output.content) for output in result.outputs]
    references = tuple(build_output_reference("image", output.address, result.created_at) for output in result.outputs)
    return io.NodeOutput([pixels for pixels, _mask in decoded], [mask for _pixels, mask in decoded], references)


class ImageGenerate(PaidNode):
    """Send one image request and return every image it made, with masks and references."""

    list_inputs = frozenset({"image"})

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the model, the image controls, the reference sockets, and the prompt."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Image: Generate",
            category=MENUS["IMAGE"],
            description="Generate or edit images with any Seedream model.",
            inputs=[
                io.String.Input(INPUT_NAMES["MODEL"], default=DEFAULT_MODELS["images"], tooltip=MODEL_TOOLTIP),
                *_CONTROLS,
                io.Image.Input(
                    "image",
                    optional=True,
                    tooltip=(
                        "Images to edit or combine: one, a batch, or a list. They come first in the prompt's Image 1, "
                        "Image 2 numbering."
                    ),
                ),
                REFERENCES_INPUT,
                *build_request_inputs(),
                io.String.Input(
                    "prompt",
                    multiline=True,
                    default="",
                    tooltip="What to draw or change. Name references as Image 1, Image 2, and so on.",
                ),
            ],
            outputs=[
                io.Image.Output("images", display_name="images", is_output_list=True),
                io.Mask.Output("masks", display_name="masks", is_output_list=True),
                io.Custom(SOCKET_TYPES["REFERENCES"]).Output("references", display_name="references"),
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
        size: str,
        max_images: int,
        background: str,
        output_format: str,
        optimize_prompt_options: str,
        watermark: bool,
        image: list[torch.Tensor] | None = None,
        references: tuple[Reference, ...] | None = None,
        options: Options | None = None,
    ) -> io.NodeOutput:
        """Wait for the request in an owned task, so ComfyUI's cancel reaches the encoding and the request."""

        async def send_encoded() -> io.NodeOutput:
            """Encode the images in a worker thread, then send the request."""
            images = await wait_for_thread(lambda: encode_sized_images(image or ()))
            request = ImageRequest(
                model_id=model.strip(),
                prompt=prompt,
                images=images,
                references=references or (),
                size=size.strip() or None,
                max_images=max_images,
                background=None if background == MODEL_DEFAULT else background,
                output_format=None if output_format == MODEL_DEFAULT else output_format,
                optimize_prompt_mode=None if optimize_prompt_options == MODEL_DEFAULT else optimize_prompt_options,
                has_watermark=watermark,
                options=options,
            )
            return await send_request(ImageOperation(request), _build_outputs, cls.hidden.unique_id)

        return await wait_for_task(asyncio.create_task(send_encoded()))


__all__ = ["ImageGenerate"]
