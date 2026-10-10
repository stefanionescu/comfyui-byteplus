"""Hyper3D and Hitem3D rows: what each 3D model reads and the 3D controls it takes."""

from ..generation.inputs import MODEL_DEFAULT

MESH_ROWS = {
    "hyper3d-gen2-260112": {
        "kinds": ("meshes",),
        "inputs": ("text", "image"),
        "outputs": ("3d",),
        "mesh": {
            "dialect": "hyper3d",
            "max_images": 5,
            "has_inline_images": True,
            # Hyper3D reads English only and cuts longer text.
            "max_prompt_characters": 400,
            "textures": ("white", "textured", "PBR"),
            "topologies": ("triangles", "quads"),
            # Hyper3D's default mesh is quads, so its default range is the quad range.
            "face_ranges": {MODEL_DEFAULT: (1_000, 200_000), "quads": (1_000, 200_000), "triangles": (500, 1_000_000)},
            "precisions": (),
            "has_pose": True,
            "has_views": False,
        },
        "sources": ("model-list", "shadoweye-create-3d-generation-task-api"),
    },
    "hitem3d-2-0-251223": {
        "kinds": ("meshes",),
        "inputs": ("image",),
        "outputs": ("3d",),
        "mesh": {
            "dialect": "hitem3d",
            "max_images": 4,
            # Hitem3D fetches images only from public addresses.
            "has_inline_images": False,
            # Its page names no prompt length, and its only example sends commands, so the row takes no prompt.
            "max_prompt_characters": 0,
            "textures": ("white", "textured"),
            "topologies": (),
            "face_ranges": {MODEL_DEFAULT: (100_000, 2_000_000)},
            "precisions": ("standard", "high"),
            "has_pose": False,
            "has_views": True,
        },
        "sources": ("model-list", "shumei-create-3d-generation-task-api"),
    },
}

__all__ = ["MESH_ROWS"]
