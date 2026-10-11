"""ModelArk's addresses, the reply limits, and the console pages messages name.

It also holds the request fields each kind of request reserves, and the service tiers Request Options offers.
"""

from .generation.inputs import MODEL_DEFAULT

# Every ModelArk request goes to Asia Pacific (Johor), the one region that serves every model the pack takes.
BASE_URL = "https://ark.ap-southeast.bytepluses.com/api/v3"

# The endpoints. Layer splitting uses the images endpoint. Video and 3D tasks share the tasks endpoint, which serves
# each task at its ID. Reading the model listing bills nothing.
ENDPOINT_URLS = {
    "chat": BASE_URL + "/chat/completions",
    "images": BASE_URL + "/images/generations",
    "tasks": BASE_URL + "/contents/generations/tasks",
    "embeddings": BASE_URL + "/embeddings/multimodal",
    "models": BASE_URL + "/models",
}

# A reply is read in chunks, and a failed one only this far.
REPLY_BYTES = {
    "CHUNK": 65_536,
    "MAX_ERROR": 65_536,
}

# A failed reply's reason is cut to this length.
MAX_REASON_CHARACTERS = 300

# A reason that ends otherwise gets a full stop.
REASON_ENDINGS = (".", "!", "?", "…")

# Console pages messages send the person to, keyed by the placeholder each message uses.
CONSOLE_URLS = {
    "activation_page": "console.byteplus.com/ark/region:ap-southeast-1/openManagement",
    "usage_page": "console.byteplus.com/ark/region:ap-southeast-1/usageTracking",
    "key_page": "console.byteplus.com/ark/region:ap-southeast-1/apiKey",
    "billing_page": "console.byteplus.com/finance/overview",
}

# The body fields an image request sets itself, whether it makes images or splits layers.
IMAGE_FIELDS = (
    "model",
    "prompt",
    "image",
    "response_format",
    "stream",
    "layer_decomposition",
    "sequential_image_generation",
    "sequential_image_generation_options",
    "service_tier",
)

# The body fields each kind of request sets itself, which extra fields may not replace.
RESERVED_FIELDS = {
    "chat": ("model", "messages", "stream", "stream_options", "service_tier"),
    "images": IMAGE_FIELDS,
    "layers": IMAGE_FIELDS,
    "videos": ("model", "content", "callback_url", "return_last_frame", "service_tier"),
    "meshes": ("model", "content", "callback_url", "service_tier"),
    "embeddings": ("model", "input", "encoding_format", "service_tier"),
}

# The service_tier dropdown: nothing sent, or ModelArk's lower-priority, lower-cost tier.
SERVICE_TIER_CHOICES = (MODEL_DEFAULT, "flex")

__all__ = [
    "BASE_URL",
    "CONSOLE_URLS",
    "ENDPOINT_URLS",
    "MAX_REASON_CHARACTERS",
    "REASON_ENDINGS",
    "REPLY_BYTES",
    "RESERVED_FIELDS",
    "SERVICE_TIER_CHOICES",
]
