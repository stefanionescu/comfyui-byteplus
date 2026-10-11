"""Messages for private settings, the API key, and state storage."""

KEY_EMPTY = "Enter a ModelArk API key of 1 to {maximum} characters without spaces at either end."

KEY_REQUIRED = "Set your ModelArk API key in BytePlus Settings or in the server's ARK_API_KEY before running."

KEY_UNREADABLE = "The saved ModelArk API key could not be read. Save the key again in BytePlus Settings."

KEY_WHITESPACE = "Remove spaces and line breaks from the ModelArk API key."

PRIVATE_STATE_LOCATION = "Keep BytePlus's private state outside ComfyUI, its package, and its media folders."

RUNTIME_NOT_READY = "The BytePlus nodes are still loading. Wait for ComfyUI to finish starting, then run again."

SETTINGS_CHANGED = "The settings changed in another window. Reload the settings and try again."

SETTINGS_RANGE = "Choose each BytePlus setting within its range."

SETTINGS_UNREADABLE = "BytePlus's private settings could not be read. Check the state folder's permissions."

SETTINGS_WHOLE_NUMBERS = "Enter whole numbers for the BytePlus settings."

SETTING_READ_ONLY = "That BytePlus setting cannot be changed here."

SETTING_UNKNOWN = "BytePlus's settings file has an unknown setting. Remove it or reset the settings."

STATE_DIRECTORY_ABSOLUTE = "Set BYTEPLUS_COMFY_STATE_DIRECTORY to an absolute folder path."

STATE_FILE_SIZE = "A BytePlus state file is larger than expected. Check the state folder."

STATE_UNREADABLE = "BytePlus's private state could not be read or written. Check the state folder's permissions."

__all__ = [
    "KEY_EMPTY",
    "KEY_REQUIRED",
    "KEY_UNREADABLE",
    "KEY_WHITESPACE",
    "PRIVATE_STATE_LOCATION",
    "RUNTIME_NOT_READY",
    "SETTINGS_CHANGED",
    "SETTINGS_RANGE",
    "SETTINGS_UNREADABLE",
    "SETTINGS_WHOLE_NUMBERS",
    "SETTING_READ_ONLY",
    "SETTING_UNKNOWN",
    "STATE_DIRECTORY_ABSOLUTE",
    "STATE_FILE_SIZE",
    "STATE_UNREADABLE",
]
