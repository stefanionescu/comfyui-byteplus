"""The node IDs the shipped workflows place, and the model IDs they choose instead of the default of a node."""

from src.config.namespace import NODE_PREFIX

CHAT_ASK = f'{NODE_PREFIX}ChatAsk'
CHAT_ATTACH_DOCUMENT = f'{NODE_PREFIX}ChatAttachDocument'
REQUEST_OPTIONS = f'{NODE_PREFIX}RequestOptions'
IMAGE_GENERATE = f'{NODE_PREFIX}ImageGenerate'
IMAGE_SPLIT_LAYERS = f'{NODE_PREFIX}ImageSplitLayers'
MODEL_REPORT = f'{NODE_PREFIX}ModelInfo'
VIDEO_GENERATE = f'{NODE_PREFIX}VideoGenerate'
VIDEO_DOWNLOAD = f'{NODE_PREFIX}VideoDownload'
REFERENCE_ADD = f'{NODE_PREFIX}ReferenceAdd'
SEARCH_EMBED = f'{NODE_PREFIX}SearchEmbed'
MESH_GENERATE = f'{NODE_PREFIX}MeshGenerate'
MESH_DOWNLOAD = f'{NODE_PREFIX}MeshDownload'
SEEDREAM_MODEL = 'seedream-4-0-250828'

__all__ = [
    'CHAT_ASK',
    'CHAT_ATTACH_DOCUMENT',
    'IMAGE_GENERATE',
    'IMAGE_SPLIT_LAYERS',
    'MESH_DOWNLOAD',
    'MESH_GENERATE',
    'MODEL_REPORT',
    'REFERENCE_ADD',
    'REQUEST_OPTIONS',
    'SEARCH_EMBED',
    'SEEDREAM_MODEL',
    'VIDEO_DOWNLOAD',
    'VIDEO_GENERATE',
]
