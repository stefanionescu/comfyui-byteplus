"""Messages for node inputs the extension refuses before sending anything."""

OPTIONS_JSON = "Write {field} as a JSON object, or leave it empty."

OPTION_FLEX = (
    "{model} does not take the flex tier. Set tier to model default in Request Options, or choose a model that "
    'takes flex; Model: Info shows "flex": true for them.'
)

OPTION_RESERVED_FIELD = "The node sets {field} itself. Remove it from the extra fields in Request Options."

OPTION_TIER_KIND = (
    "{node} requests take no service tier. Set tier to model default in the Request Options connected to it."
)

SINGLE_VALUE = "Connect one value to {name}, not a list."

__all__ = [
    "OPTIONS_JSON",
    "OPTION_FLEX",
    "OPTION_RESERVED_FIELD",
    "OPTION_TIER_KIND",
    "SINGLE_VALUE",
]
