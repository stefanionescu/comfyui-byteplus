"""Generate or edit images with any Seedream model, and keep each image's ModelArk address as a reference."""

from __future__ import annotations

import asyncio
from ..base import PaidNode
from comfy_api.latest import io
from typing import TYPE_CHECKING
from ...comfy.media import decode_image
from ...types.images import ImageRequest
from ...types.references import Reference
from datetime import UTC, datetime, timedelta
from ...byteplus.images.generate import ImageOperation
from ...config.generation.models import DEFAULT_MODELS
from ...config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES
from ...config.generation.references import OUTPUT_LIFETIME_SECONDS
from ...comfy.execution import send_request, wait_for_task, wait_for_thread
from ..inputs import REFERENCES_INPUT, encode_sized_images, build_request_inputs
from ...config.generation.inputs import INPUT_NAMES, MODEL_DEFAULT, MODEL_TOOLTIP
from ...config.generation.images import COUNT, SIZES, BACKGROUNDS, PROMPT_MODES, ASPECT_RATIOS, OUTPUT_FORMATS

if TYPE_CHECKING:
    import torch
    from ...types.options import Options
    from ...types.images import ImageResult

# The image controls; a dropdown left at model default sends nothing, except size, which sends the default tier.
_CONTROLS = (
    io.Combo.Input(
        "size",
        options=list(SIZES),
        default=MODEL_DEFAULT,
        tooltip=(
            "How large the image is. Model default is 2K. Each model takes only some sizes; Model: Info lists them."
        ),
    ),
    io.Combo.Input(
        "aspect_ratio",
        display_name="aspect ratio",
        options=list(ASPECT_RATIOS),
        default=MODEL_DEFAULT,
        tooltip="The image's shape. Model default lets the model take it from the prompt.",
    ),
    io.Int.Input(
        "count",
        default=COUNT["DEFAULT"],
        min=1,
        max=COUNT["MAX"],
        tooltip=(
            "The most images to make. Above 1, only models that make image series take it, and the prompt must ask "
            'for that many, such as "Generate 4 images of a lighthouse".'
        ),
    ),
    io.Combo.Input(
        "background",
        options=list(BACKGROUNDS),
        default=MODEL_DEFAULT,
        tooltip="Transparent keeps the transparency of one reference image that has it, and makes a PNG.",
    ),
    io.Combo.Input(
        "output_format",
        display_name="file format",
        options=list(OUTPUT_FORMATS),
        default=MODEL_DEFAULT,
        tooltip="PNG or JPEG. Model default is JPEG.",
    ),
    io.Combo.Input(
        "prompt_optimization",
        display_name="prompt optimization",
        options=list(PROMPT_MODES),
        default=MODEL_DEFAULT,
        advanced=True,
        tooltip="Fast answers sooner with slightly lower quality, on models that offer it.",
    ),
    io.Boolean.Input(
        "watermark",
        default=False,
        advanced=True,
        tooltip="Adds an AI-generated mark in the lower right corner.",
    ),
)


def _build_outputs(result: ImageResult) -> io.NodeOutput:
    """Decode each image with its mask, and keep each image's address as an image reference.

    ModelArk's created time is when it accepted the request, so a reference expires a little before its address does,
    never after.
    """
    decoded = [decode_image(output.content) for output in result.outputs]
    expires_at = datetime.fromtimestamp(result.created_at, UTC) + timedelta(seconds=OUTPUT_LIFETIME_SECONDS)
    references = tuple(Reference("image", output.address, "output", expires_at) for output in result.outputs)
    return io.NodeOutput([pixels for pixels, _mask in decoded], [mask for _pixels, mask in decoded], references)


class ImageGenerate(PaidNode):
    """Send one image request and return every image it made, with masks and references."""

    list_inputs = frozenset({"reference_images"})

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
                    "reference_images",
                    display_name="reference images",
                    optional=True,
                    tooltip=(
                        "Images to edit or combine: one, a batch, or a list. They come first in the prompt's Image 1, "
                        "Image 2 numbering."
                    ),
                ),
                REFERENCES_INPUT,
                *build_request_inputs(has_seed=False),
                io.String.Input(
                    "prompt",
                    multiline=True,
                    default="",
                    placeholder="prompt",
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
        aspect_ratio: str,
        count: int,
        background: str,
        output_format: str,
        prompt_optimization: str,
        watermark: bool,
        reference_images: list[torch.Tensor] | None = None,
        references: tuple[Reference, ...] | None = None,
        options: Options | None = None,
    ) -> io.NodeOutput:
        """Encode the reference images inside the owned task, then send the request."""

        async def send_encoded() -> io.NodeOutput:
            """Encode the reference images inside the owned task, then send the request."""
            images = await wait_for_thread(lambda: encode_sized_images(reference_images or ()))
            # A dropdown left at model default sends nothing.
            request = ImageRequest(
                model_id=model.strip(),
                prompt=prompt,
                images=images,
                references=references or (),
                size=None if size == MODEL_DEFAULT else size,
                aspect_ratio=None if aspect_ratio == MODEL_DEFAULT else aspect_ratio,
                count=count,
                background=None if background == MODEL_DEFAULT else background,
                output_format=None if output_format == MODEL_DEFAULT else output_format,
                prompt_mode=None if prompt_optimization == MODEL_DEFAULT else prompt_optimization,
                has_watermark=watermark,
                options=options,
            )
            return await send_request(ImageOperation(request), _build_outputs, cls.hidden.unique_id)

        return await wait_for_task(asyncio.create_task(send_encoded()))


__all__ = ["ImageGenerate"]
