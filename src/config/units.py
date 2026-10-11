"""Units the size and time limits are written in."""

# The settings' megabytes are mebibytes.
BYTES_PER_MEBIBYTE = 1_048_576

# ModelArk's own limits, such as its 50 MB inline video, are decimal megabytes.
BYTES_PER_MEGABYTE = 1_000_000

SECONDS_PER_MINUTE = 60

__all__ = [
    "BYTES_PER_MEBIBYTE",
    "BYTES_PER_MEGABYTE",
    "SECONDS_PER_MINUTE",
]
