"""3D requests: what one 3D: Generate run asks a 3D model to make."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .options import Options
    from .images import EncodedImage
    from .references import Reference


@dataclass(frozen=True, slots=True)
class MeshRequest:
    """One 3D request with its images already encoded.

    Attributes:
        model_id: The model ID sent to ModelArk.
        prompt: What to make and the model's own --name value commands, trimmed; empty when the model works from
            images alone.
        images: The images connected to images, in list order and then batch order.
        references: The image references, in chain order, which ModelArk reads after the images.
        options: The service tier and extra fields from Request Options.

    """

    model_id: str
    prompt: str
    images: tuple[EncodedImage, ...]
    references: tuple[Reference, ...]
    options: Options | None


__all__ = ["MeshRequest"]
