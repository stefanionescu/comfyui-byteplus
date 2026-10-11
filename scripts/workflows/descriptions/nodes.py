"""The extension's nodes that the shipped workflows place most, and the models they run beside the defaults."""

from src.config.namespace import NODE_PREFIX

CHAT_ASK = f"{NODE_PREFIX}ChatAsk"
IMAGE_GENERATE = f"{NODE_PREFIX}ImageGenerate"
VIDEO_GENERATE = f"{NODE_PREFIX}VideoGenerate"
SEED_MINI = "seed-2-0-mini-260428"
DEEPSEEK_FLASH = "deepseek-v4-flash-ga-260731"
SEEDREAM_4 = "seedream-4-0-250828"
SEEDANCE_25 = "dreamina-seedance-2-5-260628"

__all__ = [
    "CHAT_ASK",
    "DEEPSEEK_FLASH",
    "IMAGE_GENERATE",
    "SEEDANCE_25",
    "SEEDREAM_4",
    "SEED_MINI",
    "VIDEO_GENERATE",
]
