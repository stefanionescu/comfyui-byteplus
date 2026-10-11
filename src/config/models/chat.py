"""Chat model rows: what each model reads and the chat controls it takes."""

# The model list's visual understanding table, which document understanding also follows for PDF files.
VISION_INPUTS = ("text", "image", "video", "pdf")

# The model list's audio understanding table: the visual inputs and audio.
OMNI_INPUTS = ("text", "image", "video", "audio", "pdf")

# Since 2026-09-09 a text model accepts other media without reading it, and ModelArk bills the answer.
TEXT_INPUTS = ("text",)

# The pages every chat row is read from.
CHAT_PAGES = ("model-list", "chat-api", "deep-thinking", "structured-output-beta")

# The thinking.type values of a model whose thinking can be turned on and off.
THINKING = ("enabled", "disabled")

# Both structured output modes.
SCHEMAS = ("json_schema", "json_object")

# Token counts are binary thousands, as the model list writes them: 256K is 262,144.
SEED_CHAT = {
    "context": 262_144,
    "max_input": 262_144,
    "max_output": 131_072,
    "max_reasoning": 131_072,
    "default_max_tokens": 4_096,
    "thinking": THINKING,
    "has_effort": True,
    "default_effort": "medium",
}

# The DeepSeek V4 limits: 1024K context and 384K output, reasoning included.
DEEPSEEK_CHAT = {
    "context": 1_048_576,
    "max_input": 1_048_576,
    "max_output": 393_216,
    "max_reasoning": 131_072,
    "default_max_tokens": 4_096,
    "thinking": THINKING,
    "has_effort": True,
    "default_effort": "high",
    "has_temperature": True,
}

# Where the model list's tables disagree on a model's longest prompt (224K or 256K), a row takes 224K: the pack does
# not count prompt tokens, and Model: Info only reports the value.
CHAT_ROWS = {
    "dola-seed-2-1-turbo-260628": {
        "kinds": ("chat",),
        "inputs": VISION_INPUTS,
        "outputs": ("text",),
        "chat": {
            "context": 262_144,
            "max_input": 262_144,
            "max_output": 262_144,
            "max_reasoning": 262_144,
            "default_max_tokens": 4_096,
            "thinking": THINKING,
            "has_effort": True,
            # The thinking page leaves this model's default effort blank.
            "default_effort": None,
            "has_temperature": True,
            "answer_formats": SCHEMAS,
        },
        # The flex page lists this model, but ModelArk refused service_tier=flex for it on 2026-10-11.
        "sources": (*CHAT_PAGES, "document-understanding"),
    },
    "seed-2-0-lite-260428": {
        "kinds": ("chat",),
        "inputs": OMNI_INPUTS,
        "outputs": ("text",),
        "chat": {**SEED_CHAT, "has_temperature": True, "answer_formats": SCHEMAS},
        "sources": (*CHAT_PAGES, "document-understanding", "audio-understanding"),
    },
    "seed-2-0-mini-260428": {
        "kinds": ("chat",),
        "inputs": OMNI_INPUTS,
        "outputs": ("text",),
        "chat": {**SEED_CHAT, "has_temperature": True, "answer_formats": SCHEMAS},
        "sources": (*CHAT_PAGES, "document-understanding", "audio-understanding"),
    },
    "seed-2-0-pro-260328": {
        "kinds": ("chat",),
        "inputs": VISION_INPUTS,
        "outputs": ("text",),
        "chat": {**SEED_CHAT, "max_input": 229_376, "has_temperature": False, "answer_formats": ()},
        "sources": (*CHAT_PAGES, "document-understanding"),
    },
    "seed-2-0-code-preview-260328": {
        "kinds": ("chat",),
        "inputs": VISION_INPUTS,
        "outputs": ("text",),
        # The chat page lists temperature for this model, but the Responses page fixes it at 1, which ModelArk would
        # ignore without an error.
        "chat": {**SEED_CHAT, "max_input": 229_376, "has_temperature": False, "answer_formats": ()},
        "sources": (*CHAT_PAGES, "document-understanding", "create-model-responses-api"),
    },
    "seed-2-0-lite-260228": {
        "kinds": ("chat",),
        "inputs": VISION_INPUTS,
        "outputs": ("text",),
        "chat": {**SEED_CHAT, "max_input": 229_376, "has_temperature": False, "answer_formats": SCHEMAS},
        "sources": (*CHAT_PAGES, "document-understanding", "model-deprecation-notice"),
        "status": "deprecated",
        "deactivation": "2026-11-11",
        "replacement": "seed-2-0-lite-260428",
    },
    "seed-2-0-mini-260215": {
        "kinds": ("chat",),
        "inputs": VISION_INPUTS,
        "outputs": ("text",),
        "chat": {**SEED_CHAT, "max_input": 229_376, "has_temperature": True, "answer_formats": SCHEMAS},
        "sources": (*CHAT_PAGES, "document-understanding", "model-deprecation-notice"),
        "status": "deprecated",
        "deactivation": "2026-11-11",
        "replacement": "seed-2-0-mini-260428",
    },
    "glm-5-3-flash-260828": {
        "kinds": ("chat",),
        "inputs": VISION_INPUTS,
        "outputs": ("text",),
        "chat": {
            "context": 1_048_576,
            "max_input": 1_048_576,
            "max_output": 131_072,
            "max_reasoning": 131_072,
            "default_max_tokens": 4_096,
            # Its thinking cannot be turned off.
            "thinking": ("enabled",),
            "has_effort": True,
            "default_effort": "max",
            "has_temperature": True,
            "answer_formats": (),
        },
        "sources": (*CHAT_PAGES, "document-understanding"),
    },
    "glm-5-2-260617": {
        "kinds": ("chat",),
        "inputs": TEXT_INPUTS,
        "outputs": ("text",),
        "chat": {
            "context": 1_048_576,
            "max_input": 1_048_576,
            "max_output": 131_072,
            "max_reasoning": 131_072,
            "default_max_tokens": 4_096,
            "thinking": THINKING,
            "has_effort": True,
            "default_effort": "high",
            "has_temperature": True,
            "answer_formats": (),
        },
        "sources": CHAT_PAGES,
    },
    "deepseek-v4-1-flash-260910": {
        "kinds": ("chat",),
        "inputs": VISION_INPUTS,
        "outputs": ("text",),
        # The model's own page gives a 128K default answer limit, reasoning included; the model list says 4K.
        "chat": {**DEEPSEEK_CHAT, "default_max_tokens": 131_072, "answer_formats": ("json_object",)},
        "sources": (*CHAT_PAGES, "document-understanding", "deepseek-v4-1-flash"),
    },
    "deepseek-v4-pro-ga-260813": {
        "kinds": ("chat",),
        "inputs": TEXT_INPUTS,
        "outputs": ("text",),
        "chat": {**DEEPSEEK_CHAT, "answer_formats": SCHEMAS},
        "sources": (*CHAT_PAGES, "online-inference-flex"),
        "has_flex": True,
    },
    "deepseek-v4-flash-ga-260731": {
        "kinds": ("chat",),
        "inputs": TEXT_INPUTS,
        "outputs": ("text",),
        "chat": {**DEEPSEEK_CHAT, "answer_formats": SCHEMAS},
        "sources": (*CHAT_PAGES, "online-inference-flex"),
        "has_flex": True,
    },
    "deepseek-v4-pro-260425": {
        "kinds": ("chat",),
        "inputs": TEXT_INPUTS,
        "outputs": ("text",),
        "chat": {**DEEPSEEK_CHAT, "answer_formats": ()},
        "sources": CHAT_PAGES,
    },
    "deepseek-v4-flash-260425": {
        "kinds": ("chat",),
        "inputs": TEXT_INPUTS,
        "outputs": ("text",),
        # The model list says it reasons, but neither the thinking list nor the effort list names it, so it reasons by
        # its own default and takes neither control.
        "chat": {**DEEPSEEK_CHAT, "thinking": (), "has_effort": False, "default_effort": None, "answer_formats": ()},
        "sources": CHAT_PAGES,
    },
}

__all__ = ["CHAT_ROWS"]
