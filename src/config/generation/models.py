"""The default model of each kind of node."""

# Each node starts with a current, inexpensive model of its kind.
DEFAULT_MODELS = {
    "chat": "seed-2-0-lite-260428",
    "images": "dola-seedream-5-0-flash-260915",
    "layers": "dola-seedream-5-0-flash-260915",
    "videos": "dreamina-seedance-2-0-mini-260615",
    "embeddings": "skylark-embedding-vision-251215",
    "meshes": "hyper3d-gen2-260112",
}

__all__ = ["DEFAULT_MODELS"]
