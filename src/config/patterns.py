"""Regular expression text that its owners compile once."""

# A ModelArk model ID: lowercase letters, digits, dots, and hyphens; the model table decides whether it exists.
MODEL_ID_PATTERN = r"^[a-z0-9][a-z0-9.-]{0,127}$"

# The six-digit version that ends a model ID; what comes before it is the model's family.
MODEL_VERSION_PATTERN = r"-(\d{6})$"

# A video or 3D task ID: the documented "cgt-" prefix and characters that are safe in a file name and a URL path.
TASK_ID_PATTERN = r"^cgt-[0-9A-Za-z-]{1,64}$"

# Prompt text that Seedance would read as an old-style parameter command, such as "--rs 720p".
VIDEO_COMMAND_PATTERN = r"(?:^|\s)--(?:rs|resolution|rt|ratio|dur|duration|frames|seed|cf|camerafixed|wm|watermark)\b"

# A settings revision, a SHA-256 digest.
REVISION_PATTERN = r"^[a-f0-9]{64}$"

__all__ = [
    "MODEL_ID_PATTERN",
    "MODEL_VERSION_PATTERN",
    "REVISION_PATTERN",
    "TASK_ID_PATTERN",
    "VIDEO_COMMAND_PATTERN",
]
