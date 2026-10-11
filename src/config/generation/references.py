"""The kinds, origins, addresses, and lifetimes of the files ModelArk reads by address."""

# The kinds Reference: Add offers; drafts come only from video nodes.
ADDED_KINDS = ("image", "video", "audio")

# The scheme ModelArk reads asset IDs with.
ASSET_URI_PREFIX = "asset://"

# The only scheme for links and outputs.
LINK_SCHEME = "https"

# A typical web address limit; longer text is a paste mistake.
MAX_ADDRESS_CHARACTERS = 2048

# Image, video, and last-frame addresses last 24 hours.
OUTPUT_LIFETIME_SECONDS = 86_400

# A Seedance 2.5 draft task can be finished for 7 days.
DRAFT_LIFETIME_SECONDS = 604_800

# ModelArk may read the file only when a queued task starts, so a reference must last this much beyond the request.
EXPIRY_MARGIN_SECONDS = 600

__all__ = [
    "ADDED_KINDS",
    "ASSET_URI_PREFIX",
    "DRAFT_LIFETIME_SECONDS",
    "EXPIRY_MARGIN_SECONDS",
    "LINK_SCHEME",
    "MAX_ADDRESS_CHARACTERS",
    "OUTPUT_LIFETIME_SECONDS",
]
