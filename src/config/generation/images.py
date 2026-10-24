"""Image choices and limits for Image: Generate and Image: Split Layers."""

from .inputs import MODEL_DEFAULT

# Opaque is the ModelArk default, so the only other choice is `transparent`.
BACKGROUNDS = (MODEL_DEFAULT, 'transparent')

# The output_format choices.
OUTPUT_FORMATS = (MODEL_DEFAULT, 'png', 'jpeg')

# The optimize_prompt_options.mode choices.
OPTIMIZE_PROMPT_MODES = (MODEL_DEFAULT, 'standard', 'fast')

# The max_images widget; 1 turns sequential_image_generation off where the model takes it.
MAX_IMAGES = {
    'DEFAULT': 1,
    'MAX': 15,
}

# Every image request asks for addresses, because Seedance trusts a Seedream image with a real face only at its original
# address.
RESPONSE_FORMAT = 'url'

# The Split Layers size choices; every model that splits layers takes them.
LAYER_SIZES = ('auto', '1K', '1.5K', '2K')

# The default is a size billed like 1K; auto can reach 2K, which Seedream 5.0 pro bills higher.
LAYER_SIZE_DEFAULT = '1.5K'

__all__ = [
    'BACKGROUNDS',
    'LAYER_SIZES',
    'LAYER_SIZE_DEFAULT',
    'MAX_IMAGES',
    'OPTIMIZE_PROMPT_MODES',
    'OUTPUT_FORMATS',
    'RESPONSE_FORMAT',
]
