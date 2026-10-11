"""Seedream rows: sizes, references, and the image controls each model takes."""

# Every Seedream model reads a prompt and reference images.
IMAGE_INPUTS = ("text", "image")

# The pages every Seedream row is read from.
IMAGE_PAGES = ("model-list", "image-generation-api", "seedream-4-0-5-0")

# The output_format values of a model that can make PNG.
FORMATS = ("png", "jpeg")

# Seedream 5.0 pro and flash: the edit models, which make one image a request and can split it into layers.
EDIT_IMAGE = {
    "tiers": ("1K", "1.5K", "2K"),
    "default_tier": "2K",
    "pixels": (921_600, 4_624_220),
    "max_references": 10,
    "has_series": False,
    "backgrounds": ("transparent",),
    "output_formats": FORMATS,
}

# Seedream 5.0 lite, 4.5, and 4.0: the series models, whose default size, 2048x2048, is their 2K tier.
SERIES_IMAGE = {
    "default_tier": "2K",
    "max_references": 14,
    "has_series": True,
    "backgrounds": (),
}

# The pixel range of a 2K to 4K model: 2560x1440 to 4096x4096.
LARGE_PIXELS = (3_686_400, 16_777_216)

IMAGE_ROWS = {
    "dola-seedream-5-0-pro-260628": {
        "kinds": ("images", "layers"),
        "inputs": IMAGE_INPUTS,
        "outputs": ("image",),
        "image": {**EDIT_IMAGE, "prompt_modes": ("standard", "fast")},
        "sources": (*IMAGE_PAGES, "seedream-5-0-pro"),
    },
    "dola-seedream-5-0-flash-260915": {
        "kinds": ("images", "layers"),
        "inputs": IMAGE_INPUTS,
        "outputs": ("image",),
        "image": {**EDIT_IMAGE, "prompt_modes": ("standard",)},
        "sources": (*IMAGE_PAGES, "seedream-5-0-pro"),
    },
    "seedream-5-0-260128": {
        "kinds": ("images",),
        "inputs": IMAGE_INPUTS,
        "outputs": ("image",),
        "image": {
            **SERIES_IMAGE,
            "tiers": ("2K", "3K", "4K"),
            "pixels": LARGE_PIXELS,
            "output_formats": FORMATS,
            "prompt_modes": ("standard",),
        },
        "sources": IMAGE_PAGES,
    },
    "seedream-4-5-251128": {
        "kinds": ("images",),
        "inputs": IMAGE_INPUTS,
        "outputs": ("image",),
        # Seedream 4.5 and 4.0 always make JPEG and take no output_format.
        "image": {
            **SERIES_IMAGE,
            "tiers": ("2K", "4K"),
            "pixels": LARGE_PIXELS,
            "output_formats": (),
            "prompt_modes": ("standard",),
        },
        "sources": IMAGE_PAGES,
    },
    "seedream-4-0-250828": {
        "kinds": ("images",),
        "inputs": IMAGE_INPUTS,
        "outputs": ("image",),
        # The current API page takes 14 references, against 10 in an older page; a request over ModelArk's real
        # limit fails without charge.
        "image": {
            **SERIES_IMAGE,
            "tiers": ("1K", "2K", "4K"),
            "pixels": (921_600, 16_777_216),
            "output_formats": (),
            "prompt_modes": ("standard", "fast"),
        },
        "sources": IMAGE_PAGES,
    },
}

__all__ = ["IMAGE_ROWS"]
