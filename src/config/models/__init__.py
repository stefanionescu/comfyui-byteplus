"""The bundled model table: every row by model ID, aliases, source dates, and the labels the checks use."""

from .chat import CHAT_ROWS
from .meshes import MESH_ROWS
from .images import IMAGE_ROWS
from .videos import VIDEO_ROWS
from .embeddings import EMBEDDING_ROWS

# Every row by model ID.
MODEL_TABLE = {**CHAT_ROWS, **IMAGE_ROWS, **VIDEO_ROWS, **EMBEDDING_ROWS, **MESH_ROWS}

# The documented other names of a model, matched as exactly as the row they name.
ALIASES = {"seedream-5-0-lite-260128": "seedream-5-0-260128"}

# The start of an endpoint ID, which says nothing about the model behind it, so the lookup refuses it.
ENDPOINT_PREFIX = "ep-"

# The address of a BytePlus page that a row's sources name.
DOC_PAGE_URL = "https://docs.byteplus.com/en/docs/modelark/{page}"

# The kind words Model: Info shows, in the order of the node kinds.
KIND_NAMES = {
    "chat": "chat",
    "images": "image",
    "layers": "layers",
    "videos": "video",
    "meshes": "3d",
    "embeddings": "embedding",
}

# The node that sends each kind of request, in the order of the node kinds.
KIND_NODES = {
    "chat": "Chat: Ask",
    "images": "Image: Generate",
    "layers": "Image: Split Layers",
    "videos": "Video: Generate",
    "meshes": "3D: Generate",
    "embeddings": "Search: Embed",
}

# How a refusal names each kind of input.
MEDIA_LABELS = {"image": "images", "video": "video", "audio": "audio", "pdf": "PDF documents"}

# The update date of each BytePlus page a row's sources name, as the page states it.
SOURCE_DATES = {
    "model-list": "2026-09-28",
    "model-deprecation-notice": "2026-09-28",
    "chat-api": "2026-10-06",
    "deep-thinking": "2026-10-06",
    "structured-output-beta": "2026-10-06",
    "document-understanding": "2026-10-08",
    "audio-understanding": "2026-10-06",
    "online-inference-flex": "2026-09-28",
    "deepseek-v4-1-flash": "2026-10-01",
    "create-model-responses-api": "2026-10-08",
    "image-generation-api": "2026-10-10",
    "seedream-4-0-5-0": "2026-10-10",
    "seedream-5-0-pro": "2026-10-10",
    "create-video-generation-task-api": "2026-10-08",
    "video-generation-tutorial": "2026-09-28",
    "seedance-2-5": "2026-09-28",
    "seedance-2-0": "2026-09-29",
    "seedance-1-5-pro": "2026-09-28",
    "seedance-1-0-pro-pro-fast": "2026-09-28",
    "multimodal-vectorization-api": "2026-10-08",
    "vectorization": "2026-10-06",
    "shadoweye-create-3d-generation-task-api": "2026-10-08",
    "shumei-create-3d-generation-task-api": "2026-10-08",
}

__all__ = [
    "ALIASES",
    "DOC_PAGE_URL",
    "ENDPOINT_PREFIX",
    "KIND_NAMES",
    "KIND_NODES",
    "MEDIA_LABELS",
    "MODEL_TABLE",
    "SOURCE_DATES",
]
