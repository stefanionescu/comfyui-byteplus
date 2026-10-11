"""Hyper3D and Hitem3D rows: what each 3D model reads and the 3D limits it has."""

MESH_ROWS = {
    "hyper3d-gen2-260112": {
        "kinds": ("meshes",),
        "inputs": ("text", "image"),
        "mesh": {
            "format_command": "--fileformat glb",
            # Hyper3D reads English only and cuts longer text.
            "max_prompt_characters": 400,
        },
        "sources": ("model-list", "shadoweye-create-3d-generation-task-api"),
    },
    "hitem3d-2-0-251223": {
        "kinds": ("meshes",),
        "inputs": ("image",),
        "mesh": {
            "format_command": "--ff 2",
            # Its page names no text length.
            "max_prompt_characters": 0,
        },
        "sources": ("model-list", "shumei-create-3d-generation-task-api"),
    },
}

__all__ = ["MESH_ROWS"]
