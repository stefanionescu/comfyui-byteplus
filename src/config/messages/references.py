"""Messages for references the extension refuses before sending anything.

{position} counts from 1 in chain order.
"""

REFERENCE_ADDRESS_LENGTH = "Use an address of at most {maximum} characters."

REFERENCE_ASSET = (
    "Reference {position} is an asset. Only Video: Generate with a Seedance 2.5 or 2.0-series model can send assets; "
    "use an https:// address or a ModelArk output here."
)

REFERENCE_DRAFT_EXPIRED = (
    "Reference {position} is a draft that is 7 days old or nearly so, and ModelArk finishes drafts only within 7 "
    "days. Change run number on the Video: Generate node that made the draft to make a new one."
)

REFERENCE_EXPIRED = (
    "Reference {position} is a ModelArk output address that has expired or expires within {minutes} minutes; output "
    "addresses last 24 hours. Change run number on the node that made it to make it again."
)

REFERENCE_KIND = "This node takes {kinds} references; reference {position} is {kind}."

REFERENCE_REPEATED = "This file is already reference {position} in the chain."

REFERENCE_SOURCE = (
    "Enter an asset ID (asset- then 14 digits, a dash, and 5 letters or digits), the same ID after asset://, or an "
    "address that starts with https://."
)

REFERENCE_SOURCE_EMPTY = (
    "Paste a preset character's asset ID, an asset:// URI, or an https:// address into asset ID or address."
)

__all__ = [
    "REFERENCE_ADDRESS_LENGTH",
    "REFERENCE_ASSET",
    "REFERENCE_DRAFT_EXPIRED",
    "REFERENCE_EXPIRED",
    "REFERENCE_KIND",
    "REFERENCE_REPEATED",
    "REFERENCE_SOURCE",
    "REFERENCE_SOURCE_EMPTY",
]
