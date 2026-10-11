"""Messages for media that cannot be sent or read."""

AUDIO_EMPTY = "The connected audio has no samples."

AUDIO_UNWRITABLE = "The connected audio could not be written as WAV. Use mono or stereo audio."

DOWNLOAD_LIMIT = (
    "ModelArk sent a file or reply larger than the maximum download size of {maximum} MB in BytePlus settings. "
    "Raise it, or ask for a shorter or smaller output."
)

IMAGE_PIXELS = "The connected image holds values that are not numbers. Check the node that made it."

IMAGE_CHANNELS = "Connect a ComfyUI image with three or four color channels."

IMAGE_UNREADABLE = "An image ModelArk returned could not be decoded."

UPLOAD_LIMIT = (
    "The media in this request is {size} MB, above the maximum upload size of {maximum} MB in BytePlus "
    "settings. Send fewer or smaller files."
)

VIDEO_UNWRITABLE = "The connected video could not be written as MP4."

__all__ = [
    "AUDIO_EMPTY",
    "AUDIO_UNWRITABLE",
    "DOWNLOAD_LIMIT",
    "IMAGE_CHANNELS",
    "IMAGE_PIXELS",
    "IMAGE_UNREADABLE",
    "UPLOAD_LIMIT",
    "VIDEO_UNWRITABLE",
]
