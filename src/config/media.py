"""Image, audio, and video formats the extension sends to ModelArk."""

# A ComfyUI IMAGE tensor: batch, height, width, and three or four channels.
IMAGE_TENSOR = {
    "DIMENSIONS": 4,
    "RGB_CHANNELS": 3,
    "RGBA_CHANNELS": 4,
}

# Video goes inline only to chat and embedding models, as an MP4 data URL.
MP4_URL_PREFIX = "data:video/mp4;base64,"

# Audio goes as 16-bit PCM WAV: raw base64 with its format in chat, a data URL in video references.
WAV = {
    "URL_PREFIX": "data:audio/wav;base64,",
    "FORMAT": "wav",
    "CODEC": "pcm_s16le",
}

__all__ = [
    "IMAGE_TENSOR",
    "MP4_URL_PREFIX",
    "WAV",
]
