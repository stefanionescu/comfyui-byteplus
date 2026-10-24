"""Chat model rows: what each model reads and the chat controls it takes."""

# The model list's visual understanding table, which document understanding also follows for PDF files.
VISION_INPUTS = ('text', 'image', 'video', 'pdf')

# The model list's audio understanding table: the visual inputs and audio.
OMNI_INPUTS = ('text', 'image', 'video', 'audio', 'pdf')

# A text model reads only text. GLM 5.2 and the DeepSeek V4 official releases accept other media without reading it,
# and ModelArk still bills the answer.
TEXT_INPUTS = ('text',)

# The pages that every chat row comes from.
CHAT_PAGES = ('model-list', 'chat-api', 'deep-thinking', 'structured-output-beta')

# The `thinking.type` values of a model whose thinking you can turn on and off.
THINKING = ('enabled', 'disabled')

# Both structured output modes.
SCHEMAS = ('json_schema', 'json_object')

# The sampling of Seed 2.0 and later: no penalties, which the chat page says they ignore.
SEED_SAMPLING = {'temperature': 'always', 'top_p': 'always'}

# Every sampling field, as GLM takes them.
ALL_SAMPLING = {**SEED_SAMPLING, 'frequency_penalty': 'always', 'presence_penalty': 'always'}

# DeepSeek V4 Pro and Flash take the penalties only while they do not reason, and they reason by default.
DEEPSEEK_SAMPLING = {**SEED_SAMPLING, 'frequency_penalty': 'without_thinking', 'presence_penalty': 'without_thinking'}

# The stop words the DeepSeek V4.1 Flash and V4 GA models take. Every other model here reasons, and the chat page says
# reasoning models ignore stop.
DEEPSEEK_STOP = 16

# Token counts are binary thousands, as the model list writes them: 256K is 262,144.
SEED_CHAT = {
    'context': 262_144,
    'max_output': 131_072,
    'thinking': THINKING,
    'has_effort': True,
    'sampling': SEED_SAMPLING,
    'max_stop': 0,
}

# The DeepSeek V4 limits: 1024K context and 384K output, reasoning included.
DEEPSEEK_CHAT = {
    'context': 1_048_576,
    'max_output': 393_216,
    'thinking': THINKING,
    'has_effort': True,
    'sampling': DEEPSEEK_SAMPLING,
    'max_stop': 0,
}

CHAT_ROWS = {
    'dola-seed-2-1-turbo-260628': {
        'kinds': ('chat',),
        'inputs': VISION_INPUTS,
        'chat': {
            'context': 262_144,
            'max_output': 262_144,
            'thinking': THINKING,
            'has_effort': True,
            'sampling': SEED_SAMPLING,
            'max_stop': 0,
            'response_formats': SCHEMAS,
        },
        'sources': (*CHAT_PAGES, 'document-understanding'),
    },
    'seed-2-0-lite-260428': {
        'kinds': ('chat',),
        'inputs': OMNI_INPUTS,
        'chat': {**SEED_CHAT, 'response_formats': SCHEMAS},
        'sources': (*CHAT_PAGES, 'document-understanding', 'audio-understanding'),
    },
    'seed-2-0-mini-260428': {
        'kinds': ('chat',),
        'inputs': OMNI_INPUTS,
        'chat': {**SEED_CHAT, 'response_formats': SCHEMAS},
        'sources': (*CHAT_PAGES, 'document-understanding', 'audio-understanding'),
    },
    'seed-2-0-pro-260328': {
        'kinds': ('chat',),
        'inputs': VISION_INPUTS,
        # ModelArk fixes its temperature at 1 and its top_p at 0.95.
        'chat': {**SEED_CHAT, 'sampling': {}, 'response_formats': ()},
        'sources': (*CHAT_PAGES, 'document-understanding'),
    },
    'seed-2-0-code-preview-260328': {
        'kinds': ('chat',),
        'inputs': VISION_INPUTS,
        # The chat page lists temperature and top_p for this model, but the Responses page fixes them at 1 and 0.95.
        # ModelArk ignores any other value without an error.
        'chat': {**SEED_CHAT, 'sampling': {}, 'response_formats': ()},
        'sources': (*CHAT_PAGES, 'document-understanding', 'create-model-responses-api'),
    },
    'seed-2-0-lite-260228': {
        'kinds': ('chat',),
        'inputs': VISION_INPUTS,
        # ModelArk fixes its temperature at 1 and its top_p at 0.95.
        'chat': {**SEED_CHAT, 'sampling': {}, 'response_formats': SCHEMAS},
        'sources': (*CHAT_PAGES, 'document-understanding', 'model-deprecation-notice'),
        'status': 'deprecated',
        'deactivation': '2026-11-11',
        'replacement': 'seed-2-0-lite-260428',
    },
    'seed-2-0-mini-260215': {
        'kinds': ('chat',),
        'inputs': VISION_INPUTS,
        'chat': {**SEED_CHAT, 'response_formats': SCHEMAS},
        'sources': (*CHAT_PAGES, 'document-understanding', 'model-deprecation-notice'),
        'status': 'deprecated',
        'deactivation': '2026-11-11',
        'replacement': 'seed-2-0-mini-260428',
    },
    'glm-5-3-flash-260828': {
        'kinds': ('chat',),
        'inputs': VISION_INPUTS,
        'chat': {
            'context': 1_048_576,
            'max_output': 131_072,
            # You cannot turn its thinking off.
            'thinking': ('enabled',),
            'has_effort': True,
            'sampling': ALL_SAMPLING,
            'max_stop': 0,
            'response_formats': (),
        },
        'sources': (*CHAT_PAGES, 'document-understanding'),
    },
    'glm-5-2-260617': {
        'kinds': ('chat',),
        'inputs': TEXT_INPUTS,
        'chat': {
            'context': 1_048_576,
            'max_output': 131_072,
            'thinking': THINKING,
            'has_effort': True,
            'sampling': ALL_SAMPLING,
            'max_stop': 0,
            'response_formats': (),
        },
        'sources': CHAT_PAGES,
    },
    'deepseek-v4-1-flash-260910': {
        'kinds': ('chat',),
        'inputs': VISION_INPUTS,
        # It takes no penalties, and top_p only while it reasons.
        'chat': {
            **DEEPSEEK_CHAT,
            'sampling': {'temperature': 'always', 'top_p': 'with_thinking'},
            'max_stop': DEEPSEEK_STOP,
            'response_formats': ('json_object',),
        },
        'sources': (*CHAT_PAGES, 'document-understanding', 'deepseek-v4-1-flash'),
    },
    'deepseek-v4-pro-ga-260813': {
        'kinds': ('chat',),
        'inputs': TEXT_INPUTS,
        'chat': {**DEEPSEEK_CHAT, 'max_stop': DEEPSEEK_STOP, 'response_formats': SCHEMAS},
        'sources': (*CHAT_PAGES, 'online-inference-flex'),
        'has_flex': True,
    },
    'deepseek-v4-flash-ga-260731': {
        'kinds': ('chat',),
        'inputs': TEXT_INPUTS,
        'chat': {**DEEPSEEK_CHAT, 'max_stop': DEEPSEEK_STOP, 'response_formats': SCHEMAS},
        'sources': (*CHAT_PAGES, 'online-inference-flex'),
        'has_flex': True,
    },
    'deepseek-v4-pro-260425': {
        'kinds': ('chat',),
        'inputs': TEXT_INPUTS,
        'chat': {**DEEPSEEK_CHAT, 'response_formats': ()},
        'sources': CHAT_PAGES,
    },
    'deepseek-v4-flash-260425': {
        'kinds': ('chat',),
        'inputs': TEXT_INPUTS,
        # The model list says it reasons, but neither the thinking list nor the effort list names it, so it reasons by
        # its own default and takes neither control. It always reasons, so the penalties never take effect.
        'chat': {
            **DEEPSEEK_CHAT,
            'thinking': (),
            'has_effort': False,
            'sampling': SEED_SAMPLING,
            'response_formats': (),
        },
        'sources': CHAT_PAGES,
    },
}

__all__ = ['CHAT_ROWS']
