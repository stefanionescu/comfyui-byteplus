"""Units the size and time limits are written in."""

# A megabyte is 1,000,000 bytes, as ModelArk writes its limits, such as its 64 MB request body.
BYTES_PER_MEGABYTE = 1_000_000

SECONDS_PER_MINUTE = 60

__all__ = [
    "BYTES_PER_MEGABYTE",
    "SECONDS_PER_MINUTE",
]
