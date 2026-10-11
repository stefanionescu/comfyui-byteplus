"""The node IDs the shipped workflows place most, and the model IDs they choose instead of a node's default."""

from src.config.namespace import NODE_PREFIX

CHAT_ASK = f"{NODE_PREFIX}ChatAsk"
IMAGE_GENERATE = f"{NODE_PREFIX}ImageGenerate"
VIDEO_GENERATE = f"{NODE_PREFIX}VideoGenerate"
SEEDREAM_4 = "seedream-4-0-250828"

__all__ = ["CHAT_ASK", "IMAGE_GENERATE", "SEEDREAM_4", "VIDEO_GENERATE"]
