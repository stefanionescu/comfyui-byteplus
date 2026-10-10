"""Messages for node inputs the extension refuses before sending anything.

{input} is an image input's label as the node shows it, such as image or first frame. {size} is in MB of 1,000,000
bytes, rounded up to one decimal.
"""

ANSWER_SCHEMA_INVALID = "The answer schema must be a JSON object that describes the answer."

CHAT_AUDIO_SIZE = (
    "Each audio clip sent to Chat: Ask may be at most 25 MB as WAV, and one is {size} MB. Trim it, or put it at a "
    "public address and connect it with Reference: Add."
)

CHAT_BODY_SIZE = (
    "The images, videos, audio, and documents add up to {size} MB once encoded, and ModelArk takes at most 64 MB in "
    "one request. Send fewer or smaller files."
)

CHAT_IMAGE_SIZE = (
    "Each image sent to Chat: Ask may be at most 10 MB as PNG, and one is {size} MB. Shrink it with ComfyUI's Scale "
    "Image to Total Pixels; 2 megapixels is enough for most models."
)

CHAT_PDF_SIZE = "Each PDF sent to Chat: Ask may be at most 50 MB, and {name} is {size} MB. Split it into smaller files."

CHAT_VIDEO_SIZE = (
    "Each video sent to Chat: Ask may be at most 50 MB as MP4, and one is {size} MB. Trim or shrink it, or put it at "
    "a public address and connect it with Reference: Add."
)

DOCUMENT_KIND = "Choose a PDF, text, Markdown, CSV, or JSON document."

DOCUMENT_MISSING = "Put a PDF or text file in ComfyUI's input folder, press R, and choose it."

DOCUMENT_OUTSIDE = "Choose a document inside ComfyUI's input folder."

DOCUMENT_SIZE = "The document is larger than the maximum upload size of {maximum} MiB in BytePlus settings."

DOCUMENT_UNREADABLE = "The document could not be read as UTF-8 text. Save it as UTF-8 or as a PDF."

EFFORT_UNSUPPORTED = "{model} does not take a reasoning effort. Set reasoning effort to model default."

EFFORT_WITHOUT_THINKING = (
    "With thinking off, ModelArk takes only the minimal reasoning effort. Set reasoning effort to minimal or model "
    "default, or turn thinking on."
)

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

OUTPUT_TOKENS_RANGE = (
    "{model} writes at most {maximum} tokens, reasoning included. Set max tokens to {maximum} or less, or to 0."
)

PROMPT_EMPTY = "Write a prompt."

REFERENCE_IMAGE_ASSET = "The {input} input takes an image made by ModelArk or a public address, not an asset."

REFERENCE_IMAGE_SINGLE = "Connect references that hold exactly one image to {input}; they hold {count}."

SCHEMA_JSON_ONLY = (
    "{model} can answer in JSON but cannot follow a schema. Clear the answer schema and ask for JSON in the prompt, "
    "or choose a model such as seed-2-0-lite-260428."
)

SCHEMA_UNSUPPORTED = (
    "{model} cannot follow an answer schema. Clear the answer schema, or choose a model that can, such as "
    "seed-2-0-lite-260428."
)

SINGLE_VALUE = "Connect one value to {name}, not a list."

TEMPERATURE_FIXED = (
    "{model} always uses its own temperature. Set temperature to model default, or choose another model."
)

THINKING_FIXED = "{model} always thinks before answering. Set thinking to model default or on."

THINKING_UNSUPPORTED = "{model} does not let you turn thinking on or off. Set thinking to model default."

TRANSPARENT_FORMAT = "A transparent background needs the PNG file format. Set file format to png or model default."

TRANSPARENT_SOURCE = (
    "A transparent background needs exactly one reference image with transparency. Add a mask to an image with Join "
    "Image with Alpha."
)

__all__ = [
    "ANSWER_SCHEMA_INVALID",
    "CHAT_AUDIO_SIZE",
    "CHAT_BODY_SIZE",
    "CHAT_IMAGE_SIZE",
    "CHAT_PDF_SIZE",
    "CHAT_VIDEO_SIZE",
    "DOCUMENT_KIND",
    "DOCUMENT_MISSING",
    "DOCUMENT_OUTSIDE",
    "DOCUMENT_SIZE",
    "DOCUMENT_UNREADABLE",
    "EFFORT_UNSUPPORTED",
    "EFFORT_WITHOUT_THINKING",
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
    "OUTPUT_TOKENS_RANGE",
    "PROMPT_EMPTY",
    "REFERENCE_IMAGE_ASSET",
    "REFERENCE_IMAGE_SINGLE",
    "SCHEMA_JSON_ONLY",
    "SCHEMA_UNSUPPORTED",
    "SINGLE_VALUE",
    "TEMPERATURE_FIXED",
    "THINKING_FIXED",
    "THINKING_UNSUPPORTED",
    "TRANSPARENT_FORMAT",
    "TRANSPARENT_SOURCE",
]
