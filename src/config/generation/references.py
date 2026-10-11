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

# The Seedance role of each kind; a draft has none.
REFERENCE_ROLES = {
    "image": "reference_image",
    "video": "reference_video",
    "audio": "reference_audio",
}

# The Seedance content item type of each kind.
PART_TYPES = {
    "image": "image_url",
    "video": "video_url",
    "audio": "audio_url",
    "draft": "draft_task",
}

__all__ = [
    "ADDED_KINDS",
    "ASSET_URI_PREFIX",
    "DRAFT_LIFETIME_SECONDS",
    "EXPIRY_MARGIN_SECONDS",
    "LINK_SCHEME",
    "MAX_ADDRESS_CHARACTERS",
    "OUTPUT_LIFETIME_SECONDS",
    "PART_TYPES",
    "REFERENCE_ROLES",
]
