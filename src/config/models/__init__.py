"""The bundled model table: every row by model ID, families, aliases, source dates, and the labels the checks use."""

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
MEDIA_LABELS = {"text": "text", "image": "images", "video": "video", "audio": "audio", "pdf": "PDF documents"}

# Each family, the model ID without its six-digit version, mapped to its newest row, which takes another version.
# A family with a current row maps to the newest current one.
FAMILIES = {
    "dola-seed-2-1-turbo": "dola-seed-2-1-turbo-260628",
    "seed-2-0-lite": "seed-2-0-lite-260428",
    "seed-2-0-mini": "seed-2-0-mini-260428",
    "seed-2-0-pro": "seed-2-0-pro-260328",
    "seed-2-0-code-preview": "seed-2-0-code-preview-260328",
    "glm-5-3-flash": "glm-5-3-flash-260828",
    "glm-5-2": "glm-5-2-260617",
    "deepseek-v4-1-flash": "deepseek-v4-1-flash-260910",
    "deepseek-v4-pro-ga": "deepseek-v4-pro-ga-260813",
    "deepseek-v4-flash-ga": "deepseek-v4-flash-ga-260731",
    "deepseek-v4-pro": "deepseek-v4-pro-260425",
    "deepseek-v4-flash": "deepseek-v4-flash-260425",
    "dola-seedream-5-0-pro": "dola-seedream-5-0-pro-260628",
    "dola-seedream-5-0-flash": "dola-seedream-5-0-flash-260915",
    "seedream-5-0": "seedream-5-0-260128",
    "seedream-5-0-lite": "seedream-5-0-260128",
    "seedream-4-5": "seedream-4-5-251128",
    "seedream-4-0": "seedream-4-0-250828",
    "dreamina-seedance-2-5": "dreamina-seedance-2-5-260628",
    "dreamina-seedance-2-0": "dreamina-seedance-2-0-260128",
    "dreamina-seedance-2-0-fast": "dreamina-seedance-2-0-fast-260128",
    "dreamina-seedance-2-0-mini": "dreamina-seedance-2-0-mini-260615",
    "seedance-1-5-pro": "seedance-1-5-pro-251215",
    "seedance-1-0-pro": "seedance-1-0-pro-250528",
    "seedance-1-0-pro-fast": "seedance-1-0-pro-fast-251015",
    "skylark-embedding-vision": "skylark-embedding-vision-251215",
    "hyper3d-gen2": "hyper3d-gen2-260112",
    "hitem3d-2-0": "hitem3d-2-0-251223",
}

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
    "FAMILIES",
    "KIND_NAMES",
    "KIND_NODES",
    "MEDIA_LABELS",
    "MODEL_TABLE",
    "SOURCE_DATES",
]
