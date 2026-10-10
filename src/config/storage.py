"""The private state folder, its files and their size limits, and the environment variables that move them."""

# An absolute folder that replaces the platform's own state folder.
ENVIRONMENT_VARIABLES = {
    "STATE_DIRECTORY": "BYTEPLUS_COMFY_STATE_DIRECTORY",
}

__all__ = ["ENVIRONMENT_VARIABLES"]
