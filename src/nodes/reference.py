"""Add a preset character, an asset, or a public file address to the references a video, image, or chat node sends."""

from __future__ import annotations

from comfy_api.latest import io
from typing import override, TYPE_CHECKING
from ..types.errors import ErrorCode, ByteplusError
from ..config.generation.references import ADDED_KINDS
from ..byteplus.references import parse_reference_source
from ..config.messages.references import REFERENCE_REPEATED
from ..config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES

if TYPE_CHECKING:
    from ..types.references import Reference, ReferenceKind


class ReferenceAdd(io.ComfyNode):
    """Add one file ModelArk reads by address after the references it receives; it sends nothing and needs no key."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the earlier references, the file's kind, and the asset ID or address."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Reference: Add",
            category=MENUS["SHARED"],
            description=(
                "Add a preset character, an asset, or a public file address to the references a video, image, or "
                "chat node sends."
            ),
            inputs=[
                io.Custom(SOCKET_TYPES["REFERENCES"]).Input(
                    "references",
                    optional=True,
                    tooltip=(
                        "Connect another Reference: Add, or the references output of Image: Generate, Video: "
                        "Generate, or Video: Download, to add this file after them."
                    ),
                ),
                io.Combo.Input(
                    "kind",
                    options=list(ADDED_KINDS),
                    default=ADDED_KINDS[0],
                    tooltip="What the file is. A preset character is an image.",
                ),
                io.String.Input(
                    "source",
                    display_name="asset ID or address",
                    default="",
                    tooltip=(
                        "A preset character's asset ID from the ModelArk Playground (Seedance 2.5, Digital characters "
                        "tab), any asset:// URI, or a public https:// address. BytePlus allows content made with "
                        "preset characters only for trying the models and internal use."
                    ),
                ),
            ],
            outputs=[io.Custom(SOCKET_TYPES["REFERENCES"]).Output("references", display_name="references")],
        )

    @classmethod
    @override
    def execute(  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        cls, *, kind: ReferenceKind, source: str, references: tuple[Reference, ...] | None = None
    ) -> io.NodeOutput:
        """Parse the asset ID or address and add it after the earlier references.

        The same file twice would take one of the model's reference places and shift the Image 1, Image 2 numbering.
        Expiry is checked by the paid node that sends the chain, when it sends it.
        """
        earlier = references or ()
        reference = parse_reference_source(source, kind)
        for position, known in enumerate(earlier, start=1):
            if known.kind == reference.kind and known.address == reference.address:
                raise ByteplusError(ErrorCode.INVALID_INPUT, REFERENCE_REPEATED.format(position=position))
        return io.NodeOutput((*earlier, reference))


__all__ = ["ReferenceAdd"]
