"""Add a preset character, an asset, or a public address to the references a chat, image, video, or 3D node sends."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from comfy_api.latest import io

from .inputs import REFERENCES_INPUT, REFERENCES_OUTPUT
from ..state.errors import ErrorCode, BytePlusError
from ..config.namespace import MENUS, NODE_PREFIX
from ..byteplus.references import parse_reference_url
from ..config.messages.references import REFERENCE_REPEATED
from ..config.generation.references import ADDED_KINDS

if TYPE_CHECKING:
    from ..state.references import Reference, ReferenceKind


class ReferenceAdd(io.ComfyNode):
    """Add one file ModelArk reads by address after the references it receives; it sends nothing and needs no key."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """List the earlier references, the file's kind, and its asset ID or address."""
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='Reference: Add',
            category=MENUS['SHARED'],
            description=(
                'Add a preset character, an asset, or a public file address to the references a chat, image, '
                'video, or 3D node sends.'
            ),
            inputs=[
                REFERENCES_INPUT,
                io.Combo.Input(
                    'kind',
                    options=list(ADDED_KINDS),
                    default=ADDED_KINDS[0],
                    tooltip='What the file is. A preset character is an image.',
                ),
                io.String.Input(
                    'url',
                    default='',
                    tooltip=(
                        "An asset ID, such as a preset character's, with or without asset://, or a public https:// "
                        'address.'
                    ),
                ),
            ],
            outputs=[REFERENCES_OUTPUT],
        )

    @classmethod
    @override
    def execute(  # pyright: ignore[reportIncompatibleMethodOverride] # reason: ComfyUI calls by schema.
        cls, *, kind: ReferenceKind, url: str, references: tuple[Reference, ...] | None = None
    ) -> io.NodeOutput:
        """Parse the asset ID or address and add it after the earlier references.

        A repeated file takes one of the reference places of the model and shifts the Image 1, Image 2 numbering, so
        the node refuses it. The paid node that sends the chain checks expiry when it sends the chain.
        """
        earlier = references or ()
        reference = parse_reference_url(url, kind)
        for position, known in enumerate(earlier, start=1):
            if known.kind == reference.kind and known.address == reference.address:
                raise BytePlusError(ErrorCode.INVALID_INPUT, REFERENCE_REPEATED.format(position=position))
        return io.NodeOutput((*earlier, reference))


__all__ = ['ReferenceAdd']
