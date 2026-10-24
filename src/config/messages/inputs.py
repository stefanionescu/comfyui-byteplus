"""Messages for node inputs the extension refuses before sending anything.

`{input}` is the ID of an image input, such as `image` or `first_frame`. `{size}` is in MB of 1,000,000 bytes,
rounded up to one decimal. `{mode}` is what a video starts from, in the words of `VIDEO_MODE_LABELS`.
"""

DOCUMENT_KIND = 'Choose a PDF, text, Markdown, CSV, or JSON document.'

DOCUMENT_MISSING = "Put a PDF or text file in ComfyUI's input folder, press R, and choose it."

DOCUMENT_OUTSIDE = "Choose a document inside ComfyUI's input folder."

DOCUMENT_SIZE = 'The document is larger than {maximum} MB, the Maximum upload size (MB) in BytePlus Settings.'

DOCUMENT_UNREADABLE = 'The document could not be read as UTF-8 text. Save it as UTF-8 or as a PDF.'

DRAFT_ALONE = (
    'A draft keeps its own prompt and media. Clear the prompt and disconnect frames and other references to finish it.'
)

DRAFT_FINISH_SIZE = '{model} finishes drafts at {resolutions}. Set resolution to one of them.'

DRAFT_FINISH_UNSUPPORTED = '{model} cannot finish drafts. Choose the model that made the draft.'

DRAFT_SINGLE = 'Connect one draft to finish; the references hold {count}.'

DRAFT_TWICE = 'Turn off draft to finish a draft.'

EFFORT_UNSUPPORTED = '{model} does not take reasoning_effort. Set reasoning_effort to default.'

FRAMES_BESIDE_REFERENCES = (
    'A video starts from first_frame or follows reference media, not both. Disconnect one, or name a reference '
    'image as the first frame in the prompt.'
)

IMAGE_COUNT_SINGLE = (
    '{model} makes one image per run. Set max_images to 1, or choose a model that takes sequential image generation; '
    'Model: Info shows which do.'
)

IMAGE_SINGLE = 'Connect one image to {input}, not a batch or a list.'

IMAGE_SIZE = "{model} takes size {sizes}, or WIDTHxHEIGHT such as 2048x2048. Leave it empty for the model's default."

JSON_SCHEMA_INVALID = 'Write json_schema as a JSON object with a name and a schema.'

LAST_FRAME_ALONE = 'Connect first_frame with last_frame.'

MESH_FORMAT_COMMAND = (
    'The prompt asks for file format {value}, and the node returns GLB. Remove the format command, or write {command}.'
)

MESH_IMAGE_REQUIRED = '{model} needs at least one image. Connect an image reference.'

MESH_INPUT_EMPTY = 'Write a prompt, or connect images or image references to make the 3D model from.'

MESH_PROMPT_LENGTH = (
    '{model} reads at most {maximum} characters of prompt, plus the file format command the node adds. Shorten the '
    'prompt.'
)

OPTIONS_JSON = 'Write {field} as a JSON object, or leave it empty.'

OPTION_FLEX = (
    '{model} does not take the flex tier. Set service_tier to default in Request Options, or choose a model '
    'that takes flex; Model: Info shows "flex": true for them.'
)

OPTION_RESERVED_FIELD = 'The node sets {field} itself. Remove it from extra_fields in Request Options.'

PROMPT_COMMAND = (
    "Remove {command} from the prompt. ModelArk reads it as a setting; set the video's settings with the node's inputs."
)

PROMPT_EMPTY = 'Write a prompt.'

RATIO_ADAPTIVE_ONLY = '{model} keeps the shape of its input for a video from {mode}. Set ratio to adaptive or default.'

RATIO_FIXED_ONLY = '{model} cannot choose the shape of a video from {mode}. Set ratio to a shape such as 16:9.'

REFERENCE_IMAGE_SINGLE = 'Connect references that hold exactly one image to {input}; they hold {count}.'

SAMPLING_FIXED = '{model} always uses its own {field}. Set {field} to default, or choose another model.'

SAMPLING_THINKING = (
    '{model} uses {field} only with thinking set to {thinking}. Set thinking to {thinking}, or set {field} to default.'
)

SCHEMA_JSON_ONLY = (
    '{model} can answer in JSON but cannot follow a schema. Clear json_schema and ask for JSON in the prompt, '
    'or choose a model such as seed-2-0-lite-260428.'
)

SCHEMA_UNSUPPORTED = (
    '{model} cannot follow a JSON schema. Clear json_schema, or choose a model that can, such as seed-2-0-lite-260428.'
)

SEARCH_DIMENSIONS = '{model} makes vectors of {choices} values. Set dimensions to one of them, or to default.'

SEARCH_IMAGE_SHAPE = (
    'Image {number} is {width} by {height} pixels. ModelArk needs each side above 14 pixels and the long side at '
    'most 100 times the short side. Crop or resize it.'
)

SEARCH_ITEMS_EMPTY = 'Enter at least one line of text, or connect an image or a video.'

SEARCH_ITEM_STOPPED = (
    'Search: Embed stopped at item {number} of {count}; the items before it were sent and the rest were not. {message}'
)

SEARCH_TEXT_SIZE = (
    'Line {number} is longer than the 100,000 bytes ModelArk embeds as one text. Shorten it, or split it over '
    'several lines.'
)

SEARCH_VIDEO_SIZE = (
    'Video {number} is {size} MB as MP4, and ModelArk embeds videos of at most 50 MB. Trim or shrink it.'
)

SINGLE_VALUE = 'Connect one value to {name}, not a list.'

STOP_TOO_MANY = '{model} takes at most {maximum} stop words, and stop has {count}. Remove {extra}.'

STOP_UNSUPPORTED = '{model} ignores stop words. Clear stop, or choose another model.'

TASK_NEEDS_REFERENCES = (
    'With omni_reference_task_type set to {task}, the video needs reference media. Connect references or '
    'reference_image, or set omni_reference_task_type to auto.'
)

TASK_NEEDS_VIDEO = (
    'With omni_reference_task_type set to {task}, the video needs a reference video. Add one to references, or set '
    'omni_reference_task_type to reference or auto.'
)

TRANSPARENT_FORMAT = 'A transparent background needs a PNG. Set output_format to png or default.'

TRANSPARENT_SOURCE = (
    'A transparent background needs exactly one reference image with transparency. Add a mask to an image with Join '
    'Image with Alpha.'
)

VIDEO_EMPTY = 'Write a prompt, or connect first_frame or references.'

# The modes of a video request, and the edit and extend task types, as `{mode}` names them.
VIDEO_MODE_LABELS = {
    'text': 'a prompt alone',
    'first_frame': 'a first frame',
    'first_last_frame': 'first and last frames',
    'references': 'reference media',
    'edit': 'a video to edit',
    'extend': 'a video to extend',
}

VIDEO_MODE_UNSUPPORTED = '{model} cannot make a video from {mode}. Choose a model that can; Model: Info shows which do.'

__all__ = [
    'DOCUMENT_KIND',
    'DOCUMENT_MISSING',
    'DOCUMENT_OUTSIDE',
    'DOCUMENT_SIZE',
    'DOCUMENT_UNREADABLE',
    'DRAFT_ALONE',
    'DRAFT_FINISH_SIZE',
    'DRAFT_FINISH_UNSUPPORTED',
    'DRAFT_SINGLE',
    'DRAFT_TWICE',
    'EFFORT_UNSUPPORTED',
    'FRAMES_BESIDE_REFERENCES',
    'IMAGE_COUNT_SINGLE',
    'IMAGE_SINGLE',
    'IMAGE_SIZE',
    'JSON_SCHEMA_INVALID',
    'LAST_FRAME_ALONE',
    'MESH_FORMAT_COMMAND',
    'MESH_IMAGE_REQUIRED',
    'MESH_INPUT_EMPTY',
    'MESH_PROMPT_LENGTH',
    'OPTIONS_JSON',
    'OPTION_FLEX',
    'OPTION_RESERVED_FIELD',
    'PROMPT_COMMAND',
    'PROMPT_EMPTY',
    'RATIO_ADAPTIVE_ONLY',
    'RATIO_FIXED_ONLY',
    'REFERENCE_IMAGE_SINGLE',
    'SAMPLING_FIXED',
    'SAMPLING_THINKING',
    'SCHEMA_JSON_ONLY',
    'SCHEMA_UNSUPPORTED',
    'SEARCH_DIMENSIONS',
    'SEARCH_IMAGE_SHAPE',
    'SEARCH_ITEMS_EMPTY',
    'SEARCH_ITEM_STOPPED',
    'SEARCH_TEXT_SIZE',
    'SEARCH_VIDEO_SIZE',
    'SINGLE_VALUE',
    'STOP_TOO_MANY',
    'STOP_UNSUPPORTED',
    'TASK_NEEDS_REFERENCES',
    'TASK_NEEDS_VIDEO',
    'TRANSPARENT_FORMAT',
    'TRANSPARENT_SOURCE',
    'VIDEO_EMPTY',
    'VIDEO_MODE_LABELS',
    'VIDEO_MODE_UNSUPPORTED',
]
