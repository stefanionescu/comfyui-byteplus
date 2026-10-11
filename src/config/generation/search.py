"""Search: Embed choices, its instructions templates, and ModelArk's limits on one embedded item."""

from .inputs import MODEL_DEFAULT

# The vector lengths the embedding endpoint takes; model default sends none.
DIMENSIONS = (MODEL_DEFAULT, "1024", "2048")

# The instructions dropdown's input, choice, and child names: model default sends no instructions.
INSTRUCTION_CHOICE = {
    "INPUT": "instructions",
    "SEARCH": "search",
    "COMPARE": "compare",
    "TASK": "task",
}

# The task each preset starts with, from the examples in ModelArk's vectorization guide.
TASKS = {
    "search": "Find the item that best matches the given query",
    "compare": "Retrieve semantically similar content",
}

# ModelArk's fixed instructions templates, in which only the braces may change: the query, told the modalities it
# is compared with, and a search candidate, told its own modality.
INSTRUCTION_TEMPLATES = {
    "QUERY": "Target_modality: {modalities}.\nInstruction:{task}\nQuery:",
    "CANDIDATE": "Instruction:Compress the {modality} into one word.\nQuery:",
}

# The modalities an item can have, in the order the query template lists them.
MODALITIES = ("text", "image", "video")

# The query template joins several modalities with this.
MODALITY_SEPARATOR = "/"

# The longest text ModelArk embeds as one item, in UTF-8 bytes.
MAX_TEXT_BYTES = 100_000

# An image item: each side above 14 pixels, and the long side at most 100 times the short side.
IMAGE_SHAPE = {
    "MIN_SIDE": 15,
    "MAX_ASPECT": 100,
}

# ModelArk's largest video item, counted in the file's bytes; BytePlus writes MB, and 1,000,000 bytes is the smaller
# reading, so a video sent is never above the limit.
MAX_VIDEO_BYTES = 50_000_000

__all__ = [
    "DIMENSIONS",
    "IMAGE_SHAPE",
    "INSTRUCTION_CHOICE",
    "INSTRUCTION_TEMPLATES",
    "MAX_TEXT_BYTES",
    "MAX_VIDEO_BYTES",
    "MODALITIES",
    "MODALITY_SEPARATOR",
    "TASKS",
]
