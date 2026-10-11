"""Seedream rows: the sizes and the image controls each model takes."""

# Every Seedream model reads a prompt and reference images.
IMAGE_INPUTS = ("text", "image")

# The pages every Seedream row is read from.
IMAGE_PAGES = ("model-list", "image-generation-api", "seedream-4-0-5-0")

# The output_format values of a model that can make PNG.
FORMATS = ("png", "jpeg")

# Seedream 5.0 pro and flash: the edit models, which make one image a request and can split it into layers.
EDIT_IMAGE = {
    "sizes": ("1K", "1.5K", "2K"),
    "has_sequential_image_generation": False,
    "backgrounds": ("transparent",),
    "output_formats": FORMATS,
}

# Seedream 5.0 lite, 4.5, and 4.0: the models that take sequential image generation.
SEQUENTIAL_IMAGE = {
    "has_sequential_image_generation": True,
    "backgrounds": (),
}

IMAGE_ROWS = {
    "dola-seedream-5-0-pro-260628": {
        "kinds": ("images", "layers"),
        "inputs": IMAGE_INPUTS,
        "image": {**EDIT_IMAGE, "optimize_prompt_modes": ("standard", "fast")},
        "sources": (*IMAGE_PAGES, "seedream-5-0-pro"),
    },
    "dola-seedream-5-0-flash-260915": {
        "kinds": ("images", "layers"),
        "inputs": IMAGE_INPUTS,
        "image": {**EDIT_IMAGE, "optimize_prompt_modes": ("standard",)},
        "sources": (*IMAGE_PAGES, "seedream-5-0-pro"),
    },
    "seedream-5-0-260128": {
        "kinds": ("images",),
        "inputs": IMAGE_INPUTS,
        "image": {
            **SEQUENTIAL_IMAGE,
            "sizes": ("2K", "3K", "4K"),
            "output_formats": FORMATS,
            "optimize_prompt_modes": ("standard",),
        },
        "sources": IMAGE_PAGES,
    },
    "seedream-4-5-251128": {
        "kinds": ("images",),
        "inputs": IMAGE_INPUTS,
        # Seedream 4.5 and 4.0 always make JPEG and take no output_format.
        "image": {
            **SEQUENTIAL_IMAGE,
            "sizes": ("2K", "4K"),
            "output_formats": (),
            "optimize_prompt_modes": ("standard",),
        },
        "sources": IMAGE_PAGES,
    },
    "seedream-4-0-250828": {
        "kinds": ("images",),
        "inputs": IMAGE_INPUTS,
        "image": {
            **SEQUENTIAL_IMAGE,
            "sizes": ("1K", "2K", "4K"),
            "output_formats": (),
            "optimize_prompt_modes": ("standard", "fast"),
        },
        "sources": IMAGE_PAGES,
    },
}

__all__ = ["IMAGE_ROWS"]
