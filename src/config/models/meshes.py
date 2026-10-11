"""Hyper3D and Hitem3D rows: what each 3D model reads and the 3D limits it has."""

MESH_ROWS = {
    "hyper3d-gen2-260112": {
        "kinds": ("meshes",),
        "inputs": ("text", "image"),
        "mesh": {
            "dialect": "hyper3d",
            # Hyper3D reads English only and cuts longer text.
            "max_prompt_characters": 400,
        },
        "sources": ("model-list", "shadoweye-create-3d-generation-task-api"),
    },
    "hitem3d-2-0-251223": {
        "kinds": ("meshes",),
        "inputs": ("image",),
        "mesh": {
            "dialect": "hitem3d",
            # Its page names no text length.
            "max_prompt_characters": 0,
        },
        "sources": ("model-list", "shumei-create-3d-generation-task-api"),
    },
}

__all__ = ["MESH_ROWS"]
