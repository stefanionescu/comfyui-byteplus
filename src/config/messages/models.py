"""Messages for the model table checks that run before a request is sent."""

MODEL_EMPTY = "Type a model ID from the ModelArk model list."

MODEL_ENDPOINT = (
    "Use the model ID, such as {example}, instead of an endpoint ID. Copy model IDs from the ModelArk model list."
)

MODEL_FIELD = "{model} does not take {field}. Set {field} back to its default, or choose a model that takes it."

MODEL_INPUT = "{model} does not read {media}. Remove the {media}, or choose a model that does."

MODEL_KIND = "{model} does not work in {node}. Use it in {nodes}."

MODEL_RANGE = "{model} takes {field} from {minimum} to {maximum}."

MODEL_RANGE_EXTRA = "{model} takes {field} from {minimum} to {maximum}, or {extra}."

MODEL_SHUT_DOWN = "ModelArk has shut down {model}. Pick a current model from the ModelArk model list."

MODEL_UNKNOWN = (
    "{model} is not in this extension's model table. {node} takes these model families: {families}. "
    "Copy an ID from the ModelArk model list, or update the extension if the model is new."
)

MODEL_UNKNOWN_ANY = (
    "{model} is not in this extension's model table. "
    "Copy an ID from the ModelArk model list, or update the extension if the model is new."
)

MODEL_VALUE = "{model} takes {field} {values}. Choose one of these."

MODEL_VERSION = "Add the six-digit version to {model}, such as {newest}."

__all__ = [
    "MODEL_EMPTY",
    "MODEL_ENDPOINT",
    "MODEL_FIELD",
    "MODEL_INPUT",
    "MODEL_KIND",
    "MODEL_RANGE",
    "MODEL_RANGE_EXTRA",
    "MODEL_SHUT_DOWN",
    "MODEL_UNKNOWN",
    "MODEL_UNKNOWN_ANY",
    "MODEL_VALUE",
    "MODEL_VERSION",
]
