"""Register the extension's nodes in menu order."""

from comfy_api.latest import io

from .model import ModelInfo
from .search import SearchEmbed
from .options import RequestOptions
from .chat.ask import ChatAsk
from .download import MeshDownload, VideoDownload
from .reference import ReferenceAdd
from .image.layers import ImageSplitLayers
from .chat.document import ChatAttachDocument
from .mesh.generate import MeshGenerate
from .image.generate import ImageGenerate
from .video.generate import VideoGenerate

NODE_TYPES: tuple[type[io.ComfyNode], ...] = (
    ChatAsk,
    ChatAttachDocument,
    ImageGenerate,
    ImageSplitLayers,
    VideoGenerate,
    VideoDownload,
    ReferenceAdd,
    SearchEmbed,
    MeshGenerate,
    MeshDownload,
    RequestOptions,
    ModelInfo,
)

__all__ = ['NODE_TYPES']
