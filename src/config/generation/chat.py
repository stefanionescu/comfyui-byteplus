"""Chat: Ask and Chat: Attach Document choices, and ModelArk's chat limits."""

from .inputs import MODEL_DEFAULT

# The sampling fields ModelArk's Chat API takes, in node order, each as the value custom starts at, which is
# ModelArk's default, the documented minimum and maximum, and the step.
SAMPLING = {
    "temperature": (1.0, 0.0, 2.0, 0.05),
    "top_p": (0.7, 0.0, 1.0, 0.01),
    "frequency_penalty": (0.0, -2.0, 2.0, 0.05),
    "presence_penalty": (0.0, -2.0, 2.0, 0.05),
}

# What each sampling field does, for its tooltip.
SAMPLING_TOOLTIPS = {
    "temperature": "How much the answer varies.",
    "top_p": "The share of likely words the model picks from; lower keeps the answer more focused.",
    "frequency_penalty": "Above 0, the model repeats a word less the more often it has appeared.",
    "presence_penalty": "Above 0, the model repeats less any word that has appeared.",
}

# The most stop words the Chat API takes for a model that takes stop at all, when the model list names no other number.
MAX_STOP = 4

# The thinking.type values; a model's row lists the ones it takes.
THINKING_CHOICES = (MODEL_DEFAULT, "enabled", "disabled")

# How much a reasoning model thinks; a model that takes an effort takes all seven and maps them to its own levels.
EFFORTS = (MODEL_DEFAULT, "none", "minimal", "low", "medium", "high", "xhigh", "max")

# The largest max_completion_tokens the Chat API takes, though the model list names longer outputs.
MAX_COMPLETION_TOKENS = 65_536

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

# The model listing's domains of chat models. Only chat models are looked up there, since the listing lacks the
# settings the image, video, and 3D checks need.
LISTED_CHAT_DOMAINS = ("LLM", "VLM")

# The model listing's status of a model that no longer answers.
LISTED_SHUT_DOWN = "Shutdown"

__all__ = [
    "DOCUMENT_TEXT",
    "DOCUMENT_TYPES",
    "EFFORTS",
    "LISTED_CHAT_DOMAINS",
    "LISTED_SHUT_DOWN",
    "MAX_COMPLETION_TOKENS",
    "MAX_STOP",
    "PDF_MEDIA_TYPE",
    "SAMPLING",
    "SAMPLING_TOOLTIPS",
    "THINKING_CHOICES",
]
