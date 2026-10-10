"""Chat: Ask and Chat: Attach Document choices, and ModelArk's chat limits."""

from .inputs import MODEL_DEFAULT

# The temperature dropdown's input and choice names: model default sends none, and set sends its value.
TEMPERATURE_CHOICE = {
    "INPUT": "temperature",
    "SET": "set",
    "VALUE": "value",
}

# A set temperature, in ModelArk's documented range.
TEMPERATURE = {
    "DEFAULT": 1.0,
    "MAX": 2.0,
    "STEP": 0.05,
}

# Whether the model reasons; ModelArk's auto is left out, since only a retiring model takes it.
THINKING_CHOICES = (MODEL_DEFAULT, "on", "off")

# The thinking.type each choice sends.
THINKING_TYPES = {
    "on": "enabled",
    "off": "disabled",
}

# How much a reasoning model thinks; a model that takes an effort takes all seven and maps them to its own levels.
EFFORTS = (MODEL_DEFAULT, "none", "minimal", "low", "medium", "high", "xhigh", "max")

# The only effort ModelArk takes with thinking off.
THINKING_OFF_EFFORT = "minimal"

# The name an answer schema is sent under.
ANSWER_SCHEMA_NAME = "answer"

# The input_audio format of a base64 WAV clip.
AUDIO_FORMAT = "wav"

# ModelArk's largest file of each kind in a chat request, counted in the file's bytes, not its base64 text. BytePlus
# writes MB; 1,000,000 bytes is the smaller reading, so a file sent is never above its limit.
MEDIA_BYTES = {
    "image": 10_000_000,
    "video": 50_000_000,
    "audio": 25_000_000,
    "pdf": 50_000_000,
}

# ModelArk's largest request body.
MAX_BODY_BYTES = 64_000_000

# The chat reference's upper bound for max_completion_tokens, below the model list's longest outputs.
MAX_COMPLETION_TOKENS = 65_536

# ModelArk's answer limit when a request sets none; reasoning is not counted.
DEFAULT_ANSWER_TOKENS = 4_096

# A text document goes to the model as text, under its name.
DOCUMENT_TEXT = "Document {name}:\n\n{text}"

# A PDF goes as a file part; any other document goes as text.
PDF_MEDIA_TYPE = "application/pdf"

# The document files the input folder may hold, with the media type each is sent as.
DOCUMENT_TYPES = {
    ".pdf": PDF_MEDIA_TYPE,
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".csv": "text/csv",
    ".json": "application/json",
}

# The model listing's domains of chat models; its image, video, and 3D entries carry none of the parameters those
# nodes check.
LISTED_CHAT_DOMAINS = ("LLM", "VLM")

# The model listing's status of a model that no longer answers, and of one that is ending; a current model has none.
LISTED_STATUSES = {
    "SHUT_DOWN": "Shutdown",
    "RETIRING": "Retiring",
}

__all__ = [
    "ANSWER_SCHEMA_NAME",
    "AUDIO_FORMAT",
    "DEFAULT_ANSWER_TOKENS",
    "DOCUMENT_TEXT",
    "DOCUMENT_TYPES",
    "EFFORTS",
    "LISTED_CHAT_DOMAINS",
    "LISTED_STATUSES",
    "MAX_BODY_BYTES",
    "MAX_COMPLETION_TOKENS",
    "MEDIA_BYTES",
    "PDF_MEDIA_TYPE",
    "TEMPERATURE",
    "TEMPERATURE_CHOICE",
    "THINKING_CHOICES",
    "THINKING_OFF_EFFORT",
    "THINKING_TYPES",
]
