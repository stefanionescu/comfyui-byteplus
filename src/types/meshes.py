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
    """One 3D request with its images already encoded; None means model default.

    Attributes:
        model_id: The model ID sent to ModelArk.
        prompt: What to make, trimmed; empty when the model works from images alone.
        images: The images connected to images, in list order and then batch order.
        references: The image references, in chain order, which ModelArk reads after the images.
        texture: white, textured, or PBR.
        topology: triangles or quads.
        faces: The face count, or 0 for the model's default.
        precision: standard or high.
        pose: T or A pose.
        views: The side each image shows, lowercase; empty when not given.
        options: The service tier and extra fields from Request Options.

    """

    model_id: str
    prompt: str
    images: tuple[EncodedImage, ...]
    references: tuple[Reference, ...]
    texture: str | None
    topology: str | None
    faces: int
    precision: str | None
    pose: str | None
    views: tuple[str, ...]
    options: Options | None


__all__ = ["MeshRequest"]
