"""Turn text, images, and videos into embedding vectors with ModelArk and compare each item with the first."""

from __future__ import annotations

import json
import asyncio
from .base import PaidNode
from comfy_api.latest import io
from typing import cast, TYPE_CHECKING
from ..types.search import EmbeddingRequest
from ..config.namespace import MENUS, NODE_PREFIX
from ..byteplus.embeddings import EmbeddingOperation
from ..config.generation.models import DEFAULT_MODELS
from ..comfy.execution import send_request, wait_for_task, wait_for_thread
from .inputs import encode_media, encode_sized_images, build_request_inputs
from ..config.generation.search import TASKS, DIMENSIONS, INSTRUCTION_CHOICE
from ..config.generation.inputs import INPUT_NAMES, MODEL_DEFAULT, MODEL_TOOLTIP

if TYPE_CHECKING:
    import torch
    from comfy_api.latest import Input
    from ..types.options import Options
    from collections.abc import Mapping


# The instructions presets: search and compare send their task, which starts at the preset's own, and model default
# sends no instructions.
_INSTRUCTIONS = io.DynamicCombo.Input(
    INSTRUCTION_CHOICE["INPUT"],
    options=[
        *(
            io.DynamicCombo.Option(
                preset,
                [
                    io.String.Input(
                        INSTRUCTION_CHOICE["TASK"],
                        display_name="task",
                        default=TASKS[preset],
                        tooltip=(
                            "What the comparison looks for, in English, such as: Find the photo that matches this "
                            "product description."
                        ),
                    )
                ],
            )
            for preset in (INSTRUCTION_CHOICE["SEARCH"], INSTRUCTION_CHOICE["COMPARE"])
        ),
        io.DynamicCombo.Option(MODEL_DEFAULT, []),
    ],
    tooltip="How the model reads the items. Search treats the first item as the query; compare treats all items alike.",
)


def _read_instructions(choice: Mapping[str, object]) -> tuple[str | None, str]:
    """Read the instructions preset and its task; model default sends no instructions and has no task."""
    preset = cast("str", choice[INSTRUCTION_CHOICE["INPUT"]])
    if preset == MODEL_DEFAULT:
        return None, ""
    return preset, cast("str", choice[INSTRUCTION_CHOICE["TASK"]]).strip()


class SearchEmbed(PaidNode):
    """Send one embedding request per item, gathering the lists that reach the node."""

    list_inputs = frozenset({"images", "videos", "texts"})

    @classmethod
    def define_schema(cls) -> io.Schema:
        """Take input lists, so the images of one Image: Generate run are compared in one node run."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Search: Embed",
            category=MENUS["SEARCH"],
            description="Turn text, images, and videos into embedding vectors and compare each item with the first.",
            inputs=[
                io.String.Input(INPUT_NAMES["MODEL"], default=DEFAULT_MODELS["embeddings"], tooltip=MODEL_TOOLTIP),
                io.Image.Input(
                    "images",
                    optional=True,
                    tooltip="Images to compare: one, a batch, or a list. Each image is one item.",
                ),
                io.Video.Input(
                    "videos",
                    optional=True,
                    tooltip=(
                        "Videos to compare; their sound is not read. Each video is one item. Create List joins several."
                    ),
                ),
                io.Combo.Input(
                    "dimensions",
                    options=list(DIMENSIONS),
                    default=MODEL_DEFAULT,
                    advanced=True,
                    tooltip="The vector length; model default is 2048.",
                ),
                _INSTRUCTIONS,
                *build_request_inputs(has_seed=False),
                io.String.Input(
                    "texts",
                    multiline=True,
                    default="",
                    placeholder="texts",
                    tooltip="One item per line; blank lines are skipped. Put the query first.",
                ),
            ],
            outputs=[
                io.String.Output("vectors", display_name="vectors"),
                io.String.Output("similarities", display_name="similarities"),
            ],
            is_input_list=True,
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    async def send(  # noqa: PLR0913 -- reason: ComfyUI requires one named argument for each saved node input.
        cls,
        *,
        texts: list[str],
        model: str,
        dimensions: str,
        instructions: Mapping[str, object],
        images: list[torch.Tensor] | None = None,
        videos: list[Input.Video] | None = None,
        options: Options | None = None,
    ) -> io.NodeOutput:
        """Encode every image and video inside the owned task, then send the items one after another."""
        lines = tuple(line.strip() for text in texts for line in text.splitlines() if line.strip())
        preset, task = _read_instructions(instructions)

        async def send_encoded() -> io.NodeOutput:
            """Encode the media inside the owned task, then send the requests."""
            encoded_images = await wait_for_thread(lambda: encode_sized_images(images or ()))
            _image_urls, video_urls, _clips = await wait_for_thread(lambda: encode_media(None, videos, None))
            # A dropdown left at model default sends nothing.
            request = EmbeddingRequest(
                model_id=model.strip(),
                texts=lines,
                images=encoded_images,
                video_urls=video_urls,
                dimensions=None if dimensions == MODEL_DEFAULT else int(dimensions),
                instructions=preset,
                task=task,
                options=options,
            )
            return await send_request(
                EmbeddingOperation(request),
                lambda result: io.NodeOutput(
                    json.dumps([list(vector) for vector in result.vectors]), json.dumps(list(result.similarities))
                ),
                cls.hidden.unique_id,
            )

        return await wait_for_task(asyncio.create_task(send_encoded()))


__all__ = ["SearchEmbed"]
