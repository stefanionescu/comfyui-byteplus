"""Register the extension's nodes in menu order."""

from .model import ModelInfo
from .chat.ask import ChatAsk
from comfy_api.latest import io
from .options import RequestOptions
from .image.generate import ImageGenerate
from .image.layers import ImageSplitLayers
from .chat.document import ChatAttachDocument

NODE_TYPES: tuple[type[io.ComfyNode], ...] = (
    ChatAsk,
    ChatAttachDocument,
    ImageGenerate,
    ImageSplitLayers,
    RequestOptions,
    ModelInfo,
)

__all__ = ["NODE_TYPES"]
