"""The ComfyUI nodes the example workflows place beside this extension's own."""

from enum import StrEnum


class HostNode(StrEnum):
    """One ComfyUI node, by the name ComfyUI registers it under."""

    IMAGE = "LoadImage"
    AUDIO = "LoadAudio"
    PREVIEW = "PreviewAny"
    TEXT = "PrimitiveString"
    TEXT_BLOCK = "PrimitiveStringMultiline"
    FORMAT = "StringFormat"
    EXTRACT = "RegexExtract"
    NUMBER = "ComfyNumberConvert"
    MATH = "ComfyMathExpression"
    LIST_ITEM = "GetItemFromList"
    SAVE_IMAGE = "SaveImage"
    PREVIEW_IMAGE = "PreviewImage"
    JOIN_ALPHA = "JoinImageWithAlpha"
    SAVE_TEXT = "SaveText"
    SAVE_VIDEO = "SaveVideo"
    JOIN_VIDEOS = "ConcatenateVideo"


__all__ = ["HostNode"]
