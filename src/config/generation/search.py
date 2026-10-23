"""Search: Embed choices and ModelArk's limits on one embedded item."""

from .inputs import MODEL_DEFAULT

# The vector lengths the embedding endpoint takes; default sends none.
DIMENSIONS = (MODEL_DEFAULT, "1024", "2048")

# The longest text ModelArk embeds as one item, in UTF-8 bytes.
MAX_TEXT_BYTES = 100_000

# An image item: each side above 14 pixels, and the long side at most 100 times the short side.
IMAGE_SHAPE = {
    "MIN_SIDE": 15,
    "MAX_ASPECT": 100,
}

# ModelArk's largest video item, 50 MB, counted in the file's bytes.
MAX_VIDEO_BYTES = 50_000_000

__all__ = [
    "DIMENSIONS",
    "IMAGE_SHAPE",
    "MAX_TEXT_BYTES",
    "MAX_VIDEO_BYTES",
]
