"""ModelArk's addresses, the reply limits, and the console pages messages name.

It also holds the request fields each kind of request reserves, and the service tiers each kind takes.
"""

# Every ModelArk request goes to Asia Pacific (Johor), the one region that serves every model the pack takes.
BASE_URL = "https://ark.ap-southeast.bytepluses.com/api/v3"

# The endpoints; layer splitting shares images, and videos and 3D share tasks. The model listing bills nothing.
ENDPOINT_URLS = {
    "chat": BASE_URL + "/chat/completions",
    "images": BASE_URL + "/images/generations",
    "tasks": BASE_URL + "/contents/generations/tasks",
    "embeddings": BASE_URL + "/embeddings/multimodal",
    "models": BASE_URL + "/models",
}

# One video or 3D task: GET checks it, and DELETE cancels it while it is queued.
TASK_URL = BASE_URL + "/contents/generations/tasks/{task_id}"

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

# The body fields each kind of request sets itself, which extra fields may not replace.
RESERVED_FIELDS = {
    "chat": ("model", "messages", "stream", "stream_options", "service_tier"),
    "images": (
        "model",
        "prompt",
        "image",
        "response_format",
        "stream",
        "layer_decomposition",
        "sequential_image_generation",
        "sequential_image_generation_options",
        "service_tier",
    ),
    "layers": (
        "model",
        "prompt",
        "image",
        "response_format",
        "stream",
        "layer_decomposition",
        "sequential_image_generation",
        "sequential_image_generation_options",
        "service_tier",
    ),
    "videos": ("model", "content", "callback_url", "return_last_frame", "service_tier"),
    "meshes": ("model", "content", "callback_url", "service_tier"),
    "embeddings": ("model", "input", "encoding_format", "service_tier"),
}

# The service_tier values each kind of request takes; a kind missing here takes none.
TIERS = {
    "chat": ("auto", "default", "fast", "flex"),
    "videos": ("default", "flex"),
}

__all__ = [
    "BASE_URL",
    "CONSOLE_URLS",
    "ENDPOINT_URLS",
    "MAX_REASON_CHARACTERS",
    "REASON_ENDINGS",
    "REPLY_BYTES",
    "RESERVED_FIELDS",
    "TASK_URL",
    "TIERS",
]
