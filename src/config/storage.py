"""The private state folder, its files and their size limits, and the environment variables that move them."""

# The API key in the server's environment, which takes precedence over the saved key, and an absolute folder that
# replaces the platform's own state folder.
ENVIRONMENT_VARIABLES = {
    "KEY": "ARK_API_KEY",
    "STATE_DIRECTORY": "BYTEPLUS_COMFY_STATE_DIRECTORY",
}

# The state folder's name on macOS and Windows, and under XDG_STATE_HOME elsewhere.
STATE_FOLDER_NAMES = {
    "DEFAULT": "BytePlusComfyUI",
    "XDG": "byteplus-comfy",
}

# Only the folder's owner may open it.
PRIVATE_FOLDER_MODE = 0o700

# A file is written under this prefix, then moved into place.
TEMPORARY_PREFIX = ".byteplus-"

# The settings and the saved API key.
FILE_NAMES = {
    "SETTINGS": "settings.json",
    "CREDENTIAL": "credential",
}

# The video and 3D task records, one file per task ID.
JOB_FILES = {
    "FOLDER": "jobs",
    "SUFFIX": ".json",
}

# The largest settings file and task record the extension reads.
MAX_FILE_BYTES = {
    "SETTINGS": 65_536,
    "JOB": 16_384,
}

__all__ = [
    "ENVIRONMENT_VARIABLES",
    "FILE_NAMES",
    "JOB_FILES",
    "MAX_FILE_BYTES",
    "PRIVATE_FOLDER_MODE",
    "STATE_FOLDER_NAMES",
    "TEMPORARY_PREFIX",
]
