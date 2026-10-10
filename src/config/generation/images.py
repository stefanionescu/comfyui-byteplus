"""Image sizes, choices, and limits for Image: Generate and Image: Split Layers."""

from .inputs import MODEL_DEFAULT

# The size choices; model default sends the row's default tier.
SIZES = (MODEL_DEFAULT, "1K", "1.5K", "2K", "3K", "4K")

# The aspect ratios ModelArk's size tables list.
ASPECT_RATIOS = (MODEL_DEFAULT, "1:1", "4:3", "3:4", "16:9", "9:16", "3:2", "2:3", "21:9")

# Opaque is ModelArk's default, so only transparent is offered.
BACKGROUNDS = (MODEL_DEFAULT, "transparent")

# The file format choices.
OUTPUT_FORMATS = (MODEL_DEFAULT, "png", "jpeg")

# The prompt optimization choices.
PROMPT_MODES = (MODEL_DEFAULT, "standard", "fast")

# The count widget.
COUNT = {
    "DEFAULT": 1,
    "MAX": 15,
}

# References plus images made, at most, in one series request; the same for every series model.
MAX_SERIES_IMAGES = 15

# Every image request asks for addresses, which keep a Seedream output trusted by Seedance.
RESPONSE_FORMAT = "url"

# A reference image: each side above 14 pixels, and the long side at most 16 times the short side.
REFERENCE_SHAPE = {
    "MIN_SIDE": 15,
    "MAX_ASPECT": 16,
}

# The Split Layers size choices; every model that splits layers takes them.
LAYER_SIZES = ("auto", "1K", "1.5K", "2K")

# The default is a tier billed like 1K; auto can reach the 2K tier, which Seedream 5.0 pro bills higher.
LAYER_SIZE_DEFAULT = "1.5K"

# The image to split: at least 512 by 512 pixels in all, and the long side at most 16 times the short side.
LAYER_SHAPE = {
    "MIN_PIXELS": 262_144,
    "MAX_ASPECT": 16,
}

# ModelArk's width and height for each size table, tier, and aspect ratio. A row names its table and its tiers, so a
# tier a row lacks is never read. dola is Seedream 5.0 pro and flash; seedream is 5.0 lite, 4.5, and 4.0.
PIXEL_SIZES = {
    "dola": {
        "1K": {
            "1:1": "1024x1024",
            "4:3": "1152x864",
            "3:4": "864x1152",
            "16:9": "1424x800",
            "9:16": "800x1424",
            "3:2": "1248x832",
            "2:3": "832x1248",
            "21:9": "1568x672",
        },
        "1.5K": {
            "1:1": "1536x1536",
            "4:3": "1792x1344",
            "3:4": "1344x1792",
            "16:9": "2048x1152",
            "9:16": "1152x2048",
            "3:2": "1872x1248",
            "2:3": "1248x1872",
            "21:9": "2352x1008",
        },
        "2K": {
            "1:1": "2048x2048",
            "4:3": "2368x1776",
            "3:4": "1776x2368",
            "16:9": "2816x1584",
            "9:16": "1584x2816",
            "3:2": "2496x1664",
            "2:3": "1664x2496",
            "21:9": "3136x1344",
        },
    },
    "seedream": {
        # Seedream 4.0's 1K sizes; its 16:9 and 21:9 follow the API reference, the newer of two pages that disagree.
        "1K": {
            "1:1": "1024x1024",
            "4:3": "1152x864",
            "3:4": "864x1152",
            "16:9": "1280x720",
            "9:16": "720x1280",
            "3:2": "1248x832",
            "2:3": "832x1248",
            "21:9": "1512x648",
        },
        "2K": {
            "1:1": "2048x2048",
            "4:3": "2304x1728",
            "3:4": "1728x2304",
            "16:9": "2848x1600",
            "9:16": "1600x2848",
            "3:2": "2496x1664",
            "2:3": "1664x2496",
            "21:9": "3136x1344",
        },
        "3K": {
            "1:1": "3072x3072",
            "4:3": "3456x2592",
            "3:4": "2592x3456",
            "16:9": "4096x2304",
            "9:16": "2304x4096",
            "3:2": "3744x2496",
            "2:3": "2496x3744",
            "21:9": "4704x2016",
        },
        "4K": {
            "1:1": "4096x4096",
            "4:3": "4704x3520",
            "3:4": "3520x4704",
            "16:9": "5504x3040",
            "9:16": "3040x5504",
            "3:2": "4992x3328",
            "2:3": "3328x4992",
            "21:9": "6240x2656",
        },
    },
}

__all__ = [
    "ASPECT_RATIOS",
    "BACKGROUNDS",
    "COUNT",
    "LAYER_SHAPE",
    "LAYER_SIZES",
    "LAYER_SIZE_DEFAULT",
    "MAX_SERIES_IMAGES",
    "OUTPUT_FORMATS",
    "PIXEL_SIZES",
    "PROMPT_MODES",
    "REFERENCE_SHAPE",
    "RESPONSE_FORMAT",
    "SIZES",
]
