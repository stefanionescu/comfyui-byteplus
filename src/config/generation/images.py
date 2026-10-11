"""Image choices and limits for Image: Generate and Image: Split Layers."""

from .inputs import MODEL_DEFAULT

# Opaque is ModelArk's default, so only transparent is offered.
BACKGROUNDS = (MODEL_DEFAULT, "transparent")

# The output_format choices.
OUTPUT_FORMATS = (MODEL_DEFAULT, "png", "jpeg")

# The optimize_prompt_options.mode choices.
PROMPT_MODES = (MODEL_DEFAULT, "standard", "fast")

# The max_images widget; 1 turns a series model's sequential_image_generation off.
MAX_IMAGES = {
    "DEFAULT": 1,
    "MAX": 15,
}

# Every image request asks for addresses, which keep a Seedream output trusted by Seedance.
RESPONSE_FORMAT = "url"

# The Split Layers size choices; every model that splits layers takes them.
LAYER_SIZES = ("auto", "1K", "1.5K", "2K")

# The default is a tier billed like 1K; auto can reach the 2K tier, which Seedream 5.0 pro bills higher.
LAYER_SIZE_DEFAULT = "1.5K"

__all__ = [
    "BACKGROUNDS",
    "LAYER_SIZES",
    "LAYER_SIZE_DEFAULT",
    "MAX_IMAGES",
    "OUTPUT_FORMATS",
    "PROMPT_MODES",
    "RESPONSE_FORMAT",
]
