"""Turn text, images, and videos into embedding vectors with ModelArk and compare each item with the first."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, override

from comfy_api.latest import io

from .base import PaidNode
from .inputs import encode_sized_images, build_request_inputs
from ..comfy.media import encode_video
from ..state.search import EmbeddingRequest
from ..comfy.execution import send_request, wait_for_thread
from ..config.namespace import MENUS, NODE_PREFIX
from ..byteplus.embeddings import EmbeddingOperation
from ..config.generation.inputs import INPUT_NAMES, MODEL_DEFAULT, MODEL_TOOLTIP
from ..config.generation.models import DEFAULT_MODELS
from ..config.generation.search import DIMENSIONS

if TYPE_CHECKING:
    import torch
    from comfy_api.latest import Input

    from ..state.options import Options


class SearchEmbed(PaidNode):
    """Send one embedding request per item, gathering the lists that reach the node."""

    list_inputs = frozenset({'images', 'videos', 'texts'})

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Take input lists, so one node run compares the images of one Image: Generate run."""
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='Search: Embed',
            category=MENUS['SEARCH'],
            description='Turn text, images, and videos into embedding vectors and compare each item with the first.',
            is_input_list=True,
            hidden=[io.Hidden.unique_id],
            inputs=[
                io.String.Input(INPUT_NAMES['MODEL'], default=DEFAULT_MODELS['embeddings'], tooltip=MODEL_TOOLTIP),
                io.Image.Input(
                    'images',
                    optional=True,
                    tooltip='Images to compare: one, a batch, or a list. Each image is one item.',
                ),
                io.Video.Input(
                    'videos',
                    optional=True,
                    tooltip=(
                        'Videos to compare; their sound is not read. Each video is one item. Create List joins several.'
                    ),
                ),
                io.Combo.Input(
                    'dimensions',
                    options=list(DIMENSIONS),
                    default=MODEL_DEFAULT,
                    advanced=True,
                    tooltip='The vector length; default is 2048.',
                ),
                *build_request_inputs(),
                io.String.Input(
                    'instructions',
                    multiline=True,
                    default='',
                    tooltip=(
                        "Sent as ModelArk's instructions field with every item; write it in ModelArk's form, such as "
                        'Target_modality: image.\nInstruction:…\nQuery:'
                    ),
                ),
                io.String.Input(
                    'texts',
                    multiline=True,
                    default='',
                    tooltip='One item per line; blank lines are skipped. Put the query first.',
                ),
            ],
            outputs=[
                io.String.Output('vectors', display_name='vectors'),
                io.String.Output('similarities', display_name='similarities'),
            ],
        )

    @classmethod
    @override
    async def send(
        cls,
        *,
        texts: list[str],
        model: str,
        dimensions: str,
        instructions: str,
        images: list[torch.Tensor] | None = None,
        videos: list[Input.Video] | None = None,
        options: Options | None = None,
    ) -> io.NodeOutput:
        """Encode every image and video in a worker thread, then send the items one after another."""
        lines = tuple(line.strip() for text in texts for line in text.splitlines() if line.strip())
        encoded_images, video_urls = await wait_for_thread(
            lambda: (encode_sized_images(images or ()), tuple(encode_video(video) for video in videos or ()))
        )
        # A dropdown left at default sends nothing.
        request = EmbeddingRequest(
            model_id=model.strip(),
            texts=lines,
            images=encoded_images,
            video_urls=video_urls,
            dimensions=None if dimensions == MODEL_DEFAULT else int(dimensions),
            instructions=instructions if instructions.strip() else None,
            options=options,
        )
        operation = EmbeddingOperation(request)
        return await send_request(
            operation.validate,
            operation.send,
            lambda result: io.NodeOutput(
                json.dumps([list(vector) for vector in result.vectors]), json.dumps(list(result.similarities))
            ),
            cls.hidden.unique_id,
        )


__all__ = ['SearchEmbed']
