"""Messages for node inputs the extension refuses before sending anything.

{input} is an image input's label as the node shows it, such as image or first frame.
"""

IMAGE_COUNT_SINGLE = (
    "{model} makes one image per run. Set count to 1, or choose a model that makes image series; Model: Info shows "
    "which do."
)

IMAGE_COUNT_TOTAL = (
    "Reference images and count together can be at most 15, and they are {total}. Lower count or connect fewer "
    "references."
)

IMAGE_REFERENCE_LIMIT = "{model} takes at most {maximum} reference images, and {count} are connected."

IMAGE_REFERENCE_SHAPE = (
    "A reference image is {width} by {height} pixels. Seedream needs each side above 14 pixels and the long side at "
    "most 16 times the short side. Crop or resize it."
)

IMAGE_SINGLE = "Connect one image to {input}, not a batch or a list."

LAYER_IMAGE_SIZE = (
    "The image to split is {width} by {height} pixels. It needs at least 262,144 pixels in all, such as 512 by 512, "
    "and its long side at most 16 times the short side. Resize it with Scale Image to Total Pixels."
)

OPTIONS_JSON = "Write {field} as a JSON object, or leave it empty."

OPTION_FLEX = (
    "{model} does not take the flex tier. Set tier to model default in Request Options, or choose a model that "
    'takes flex; Model: Info shows "flex": true for them.'
)

OPTION_RESERVED_FIELD = "The node sets {field} itself. Remove it from the extra fields in Request Options."

OPTION_TIER_KIND = (
    "{node} requests take no service tier. Set tier to model default in the Request Options connected to it."
)

PROMPT_EMPTY = "Write a prompt."

REFERENCE_IMAGE_ASSET = "The {input} input takes an image made by ModelArk or a public address, not an asset."

REFERENCE_IMAGE_SINGLE = "Connect references that hold exactly one image to {input}; they hold {count}."

SINGLE_VALUE = "Connect one value to {name}, not a list."

TRANSPARENT_FORMAT = "A transparent background needs the PNG file format. Set file format to png or model default."

TRANSPARENT_SOURCE = (
    "A transparent background needs exactly one reference image with transparency. Add a mask to an image with Join "
    "Image with Alpha."
)

__all__ = [
    "IMAGE_COUNT_SINGLE",
    "IMAGE_COUNT_TOTAL",
    "IMAGE_REFERENCE_LIMIT",
    "IMAGE_REFERENCE_SHAPE",
    "IMAGE_SINGLE",
    "LAYER_IMAGE_SIZE",
    "OPTIONS_JSON",
    "OPTION_FLEX",
    "OPTION_RESERVED_FIELD",
    "OPTION_TIER_KIND",
    "PROMPT_EMPTY",
    "REFERENCE_IMAGE_ASSET",
    "REFERENCE_IMAGE_SINGLE",
    "SINGLE_VALUE",
    "TRANSPARENT_FORMAT",
    "TRANSPARENT_SOURCE",
]
