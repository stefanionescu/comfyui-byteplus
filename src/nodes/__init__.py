"""Register the extension's nodes in menu order."""

from .model import ModelInfo
from comfy_api.latest import io
from .options import RequestOptions

NODE_TYPES: tuple[type[io.ComfyNode], ...] = (
    RequestOptions,
    ModelInfo,
)

__all__ = ["NODE_TYPES"]
