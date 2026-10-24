"""Regular expression text that its owners compile once."""

# A ModelArk model ID: lowercase letters, digits, dots, and hyphens; the model table decides whether it exists.
MODEL_ID_PATTERN = r'^[a-z0-9][a-z0-9.-]{0,127}$'

# The six-digit version that ends a model ID; what comes before it is the model's family.
MODEL_VERSION_PATTERN = r'-(\d{6})$'

# A Seedream size in pixels, as WIDTHxHEIGHT; group 1 is the width and group 2 the height.
IMAGE_SIZE_PATTERN = r'^([1-9][0-9]*)x([1-9][0-9]*)$'

# A video or 3D task ID: the documented "cgt-" prefix and characters that are safe in a file name and a URL path.
TASK_ID_PATTERN = r'^cgt-[0-9A-Za-z-]{1,64}$'

# A preset or private asset ID, alone or after `asset://`. The owner compiles it case-insensitively, because the
# BytePlus API reference writes `Asset-2026…` and the Playground writes `asset-2026…`. Group 1 is the ID as typed.
ASSET_ID_PATTERN = r'^(?:asset://)?(asset-\d{14}-[a-z0-9]{5})$'

# Prompt text that Seedance reads as an old-style parameter command, such as `--rs 720p`.
VIDEO_COMMAND_PATTERN = r'(?:^|\s)--(?:rs|resolution|rt|ratio|dur|duration|frames|seed|cf|camerafixed|wm|watermark)\b'

# A 3D file format command in prompt text, such as `--fileformat obj` or `--ff 1`; group 1 is the value. The owner
# compiles it case-insensitively.
MESH_FORMAT_COMMAND_PATTERN = r'(?:^|\s)--(?:fileformat|ff)\s+(\S+)'

# A settings revision, a SHA-256 digest.
REVISION_PATTERN = r'^[a-f0-9]{64}$'

# The extension cleans the reason of a failed reply before a person reads it. Console addresses stay, without the
# scheme. The extension removes other addresses, the ModelArk request ID, and key-shaped text. Key-shaped text is a
# universally unique identifier (UUID), an `ark-` key, or a long run of letters, digits, and base64 signs. Such a run
# has 32 or more signs and holds both a letter and a digit. `FREE_TRIAL` separates the two `QuotaExceeded` replies
# of ModelArk.
REASON_PATTERNS = {
    'CONSOLE_URL': r'https://(console\.byteplus\.com/\S*?)(?=[.,;:]?(?:\s|$))',
    'URL': r'https?://\S+',
    'REQUEST_ID': r'(?i)\s*request id\s*:\s*[0-9A-Za-z-]*\.?',
    'KEY': (
        r'\b[0-9A-Fa-f]{8}(?:-[0-9A-Fa-f]{4}){3}-[0-9A-Fa-f]{12}\b'
        r'|\bark-[\w-]{16,}'
        r'|(?<![\w+/=-])(?=[\w+/=]*\d)(?=[\w+/=]*[A-Za-z])[\w+/=]{32,}'
    ),
    'FREE_TRIAL': r'(?i)\bfree trial\b',
}

__all__ = [
    'ASSET_ID_PATTERN',
    'IMAGE_SIZE_PATTERN',
    'MESH_FORMAT_COMMAND_PATTERN',
    'MODEL_ID_PATTERN',
    'MODEL_VERSION_PATTERN',
    'REASON_PATTERNS',
    'REVISION_PATTERN',
    'TASK_ID_PATTERN',
    'VIDEO_COMMAND_PATTERN',
]
