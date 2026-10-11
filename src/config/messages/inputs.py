"""Messages for node inputs the extension refuses before sending anything.

{input} is an image input's label as the node shows it, such as image or first frame. {size} is in MB of 1,000,000
bytes, rounded up to one decimal. {mode} is what a video starts from, in the words of VIDEO_MODE_LABELS, {kind} is
image, video, or audio, and {seconds} has one decimal.
"""

AUDIO_LENGTH = "{model} takes reference audio clips of {minimum} to {maximum} seconds; one is {seconds} seconds."

AUDIO_NEEDS_MEDIA = "{model} needs a reference image or video beside reference audio."

AUDIO_TOTAL = (
    "{model} takes at most {maximum} seconds of reference audio in all; the connected clips add up to {seconds} "
    "seconds."
)

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

DRAFT_ALONE = (
    "A draft keeps its own prompt and media. Clear the prompt and disconnect frames and other references to finish it."
)

DRAFT_FINISH_SIZE = "{model} finishes drafts at {resolutions}. Set resolution to one of them."

DRAFT_FINISH_UNSUPPORTED = "{model} cannot finish drafts. Choose the model that made the draft."

DRAFT_REUSED = (
    "Finishing a draft keeps its ratio, sound, task type, and camera. Set ratio and generate audio to model default, "
    "omni reference task type to auto, and camera fixed off."
)

DRAFT_SINGLE = "Connect one draft to finish; the references hold {count}."

DRAFT_TWICE = "Turn off draft to finish a draft."

EFFORT_UNSUPPORTED = "{model} does not take a reasoning effort. Set reasoning effort to model default."

EFFORT_WITHOUT_THINKING = (
    "With thinking disabled, ModelArk takes only the minimal reasoning effort. Set reasoning effort to minimal or "
    "model default, or set thinking to enabled."
)

FRAMES_BESIDE_REFERENCES = (
    "A video starts from frames or follows reference media, not both. Disconnect one, or name a reference image as "
    "the first frame in the prompt."
)

IMAGE_COUNT_SINGLE = (
    "{model} makes one image per run. Set max images to 1, or choose a model that makes image series; Model: Info "
    "shows which do."
)

IMAGE_COUNT_TOTAL = (
    "Reference images and max images together can be at most 15, and they are {total}. Lower max images or connect "
    "fewer references."
)

IMAGE_REFERENCE_LIMIT = "{model} takes at most {maximum} reference images, and {count} are connected."

IMAGE_REFERENCE_SHAPE = (
    "A reference image is {width} by {height} pixels. Seedream needs each side above 14 pixels and the long side at "
    "most 16 times the short side. Crop or resize it."
)

IMAGE_SINGLE = "Connect one image to {input}, not a batch or a list."

IMAGE_SIZE = (
    "{model} takes size {tiers}, or WIDTHxHEIGHT such as 2048x2048: {minimum} to {maximum} pixels in all, with the "
    "long side at most 16 times the short side. Leave it empty for the model's default."
)

JSON_SCHEMA_INVALID = "Write the JSON schema as a JSON object with a name and a schema."

LAST_FRAME_ALONE = "Connect a first frame with the last frame."

LAYER_IMAGE_SIZE = (
    "The image to split is {width} by {height} pixels. It needs at least 262,144 pixels in all, such as 512 by 512, "
    "and its long side at most 16 times the short side. Resize it with Scale Image to Total Pixels."
)

MESH_FORMAT_COMMAND = (
    "The prompt asks for file format {value}, and the node returns GLB. Remove the format command, or write {command}."
)

MESH_IMAGES_ADDRESS_ONLY = (
    "{model} reads images only from public addresses. Connect them to references instead, for example Image: "
    "Generate's references output or Reference: Add."
)

MESH_IMAGE_COUNT = (
    "{model} takes at most {maximum} images, and {count} are connected. Connect fewer images and image references."
)

MESH_IMAGE_PIXELS = (
    "Image {number} is {width} by {height} pixels, and ModelArk takes 3D source images of fewer than 4096 by 4096 "
    "pixels. Shrink it with ComfyUI's Scale Image to Total Pixels."
)

MESH_IMAGE_REQUIRED = "{model} needs at least one image. Connect an image reference."

MESH_IMAGE_SIZE = (
    "Image {number} is {size} MB as PNG, and ModelArk takes 3D source images under 30 MB. Shrink it with ComfyUI's "
    "Scale Image to Total Pixels."
)

MESH_INPUT_EMPTY = "Write a prompt, or connect images or image references to make the 3D model from."


MESH_PROMPT_LENGTH = (
    "{model} reads at most {maximum} characters of prompt, beside the file format command the node adds. Shorten the "
    "prompt."
)


OPTIONS_JSON = "Write {field} as a JSON object, or leave it empty."

OPTION_FLEX = (
    "{model} does not take the flex tier. Set service tier to model default in Request Options, or choose a model "
    'that takes flex; Model: Info shows "flex": true for them.'
)

OPTION_RESERVED_FIELD = "The node sets {field} itself. Remove it from the extra fields in Request Options."

OPTION_TIER_KIND = (
    "{node} requests take no service tier. Set service tier to model default in the Request Options connected to it."
)

OUTPUT_TOKENS_RANGE = (
    "{model} writes at most {maximum} tokens, reasoning included. Set max completion tokens to {maximum} or less, or "
    "to 0."
)

PROMPT_COMMAND = (
    "Remove {command} from the prompt. ModelArk reads it as a setting; set the video's settings with the node's inputs."
)

PROMPT_EMPTY = "Write a prompt."

RATIO_ADAPTIVE_ONLY = (
    "{model} keeps the shape of its input for a video from {mode}. Set ratio to adaptive or model default."
)

RATIO_FIXED_ONLY = "{model} cannot choose the shape of a video from {mode}. Set ratio to a shape such as 16:9."

REFERENCE_IMAGE_ASSET = "The {input} input takes an image made by ModelArk or a public address, not an asset."

REFERENCE_IMAGE_SINGLE = "Connect references that hold exactly one image to {input}; they hold {count}."

SCHEMA_JSON_ONLY = (
    "{model} can answer in JSON but cannot follow a schema. Clear the JSON schema and ask for JSON in the prompt, "
    "or choose a model such as seed-2-0-lite-260428."
)

SCHEMA_UNSUPPORTED = (
    "{model} cannot follow a JSON schema. Clear the JSON schema, or choose a model that can, such as "
    "seed-2-0-lite-260428."
)

SEARCH_DIMENSIONS = "{model} makes vectors of {choices} values. Set dimensions to one of them, or to model default."

SEARCH_IMAGE_SHAPE = (
    "Image {number} is {width} by {height} pixels. ModelArk needs each side above 14 pixels and the long side at "
    "most 100 times the short side. Crop or resize it."
)

SEARCH_ITEMS_EMPTY = "Enter at least one line of text, or connect an image or a video."

SEARCH_ITEM_STOPPED = (
    "Search: Embed stopped at item {number} of {count}; the items before it were sent and the rest were not. {message}"
)


SEARCH_TEXT_SIZE = (
    "Line {number} is longer than the 100,000 bytes ModelArk embeds as one text. Shorten it, or split it over "
    "several lines."
)

SEARCH_VIDEO_SIZE = (
    "Video {number} is {size} MB as MP4, and ModelArk embeds videos of at most 50 MB. Trim or shrink it."
)

SINGLE_VALUE = "Connect one value to {name}, not a list."

TASK_NEEDS_REFERENCES = (
    "Omni reference task type {task} needs reference media. Connect references or reference image, or set omni "
    "reference task type to auto."
)

TASK_NEEDS_VIDEO = (
    "Omni reference task type {task} needs a reference video. Add one to references, or set omni reference task type "
    "to reference or auto."
)

TEMPERATURE_FIXED = (
    "{model} always uses its own temperature. Set temperature to model default, or choose another model."
)


TRANSPARENT_FORMAT = "A transparent background needs a PNG. Set output format to png or model default."

TRANSPARENT_SOURCE = (
    "A transparent background needs exactly one reference image with transparency. Add a mask to an image with Join "
    "Image with Alpha."
)

VIDEO_EMPTY = "Write a prompt, or connect a first frame or references."

VIDEO_IMAGE_SIZE = (
    "An image for {input} is {width} by {height} pixels. Seedance needs each side from 300 to 6,000 pixels and the "
    "long side at most 2.5 times the short side. Crop or resize it."
)

# The modes of a video request, and the edit and extend task types, as {mode} names them.
VIDEO_MODE_LABELS = {
    "text": "a prompt alone",
    "first_frame": "a first frame",
    "first_last_frame": "first and last frames",
    "references": "reference media",
    "edit": "a video to edit",
    "extend": "a video to extend",
}

VIDEO_MODE_UNSUPPORTED = "{model} cannot make a video from {mode}. Choose a model that can; Model: Info shows which do."

VIDEO_REFERENCE_LIMIT = "{model} takes at most {maximum} {kind} references, and {count} are connected."

__all__ = [
    "AUDIO_LENGTH",
    "AUDIO_NEEDS_MEDIA",
    "AUDIO_TOTAL",
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
    "DRAFT_ALONE",
    "DRAFT_FINISH_SIZE",
    "DRAFT_FINISH_UNSUPPORTED",
    "DRAFT_REUSED",
    "DRAFT_SINGLE",
    "DRAFT_TWICE",
    "EFFORT_UNSUPPORTED",
    "EFFORT_WITHOUT_THINKING",
    "FRAMES_BESIDE_REFERENCES",
    "IMAGE_COUNT_SINGLE",
    "IMAGE_COUNT_TOTAL",
    "IMAGE_REFERENCE_LIMIT",
    "IMAGE_REFERENCE_SHAPE",
    "IMAGE_SINGLE",
    "IMAGE_SIZE",
    "JSON_SCHEMA_INVALID",
    "LAST_FRAME_ALONE",
    "LAYER_IMAGE_SIZE",
    "MESH_FORMAT_COMMAND",
    "MESH_IMAGES_ADDRESS_ONLY",
    "MESH_IMAGE_COUNT",
    "MESH_IMAGE_PIXELS",
    "MESH_IMAGE_REQUIRED",
    "MESH_IMAGE_SIZE",
    "MESH_INPUT_EMPTY",
    "MESH_PROMPT_LENGTH",
    "OPTIONS_JSON",
    "OPTION_FLEX",
    "OPTION_RESERVED_FIELD",
    "OPTION_TIER_KIND",
    "OUTPUT_TOKENS_RANGE",
    "PROMPT_COMMAND",
    "PROMPT_EMPTY",
    "RATIO_ADAPTIVE_ONLY",
    "RATIO_FIXED_ONLY",
    "REFERENCE_IMAGE_ASSET",
    "REFERENCE_IMAGE_SINGLE",
    "SCHEMA_JSON_ONLY",
    "SCHEMA_UNSUPPORTED",
    "SEARCH_DIMENSIONS",
    "SEARCH_IMAGE_SHAPE",
    "SEARCH_ITEMS_EMPTY",
    "SEARCH_ITEM_STOPPED",
    "SEARCH_TEXT_SIZE",
    "SEARCH_VIDEO_SIZE",
    "SINGLE_VALUE",
    "TASK_NEEDS_REFERENCES",
    "TASK_NEEDS_VIDEO",
    "TEMPERATURE_FIXED",
    "TRANSPARENT_FORMAT",
    "TRANSPARENT_SOURCE",
    "VIDEO_EMPTY",
    "VIDEO_IMAGE_SIZE",
    "VIDEO_MODE_LABELS",
    "VIDEO_MODE_UNSUPPORTED",
    "VIDEO_REFERENCE_LIMIT",
]
