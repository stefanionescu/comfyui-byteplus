"""Seedance rows: task modes, references, and the video controls each model takes."""

# Seedance 2.x reads a prompt, frames, and reference images, videos, and audio.
REFERENCE_INPUTS = ("text", "image", "video", "audio")

# Seedance 1.x reads a prompt and frames.
FRAME_INPUTS = ("text", "image")

# Every way a task can start: a prompt alone, a first frame, first and last frames, or references.
ALL_MODES = ("text", "first_frame", "first_last_frame", "references")

# The modes of a model that takes no references.
FRAME_MODES = ("text", "first_frame", "first_last_frame")

# The pages every Seedance row is read from.
VIDEO_PAGES = ("model-list", "create-video-generation-task-api", "video-generation-tutorial")

# The Seedance 2.0 series. The API page lists seed only for the 1.x models, and the console's Seedance 2.5 schema
# marks it unsupported, so no 2.x row takes it.
SERIES_VIDEO = {
    "modes": ALL_MODES,
    "durations": (4, 15),
    "can_choose_duration": True,
    "adaptive_modes": (),
    "fixed_ratio_modes": (),
    "has_audio": True,
    "has_seed": False,
    "has_fixed_camera": False,
    "output_formats": (),
    "omni_reference_task_types": (),
    "draft_resolutions": (),
}

# Seedance 1.0 pro, which makes no sound and takes no adaptive ratio from a prompt alone.
PRO_VIDEO = {
    "modes": FRAME_MODES,
    "resolutions": ("480p", "720p", "1080p"),
    "durations": (2, 12),
    "can_choose_duration": False,
    "adaptive_modes": (),
    "fixed_ratio_modes": ("text",),
    "has_audio": False,
    "has_seed": True,
    "has_fixed_camera": True,
    "output_formats": (),
    "omni_reference_task_types": (),
    "draft_resolutions": (),
}

VIDEO_ROWS = {
    "dreamina-seedance-2-5-260628": {
        "kinds": ("videos",),
        "inputs": REFERENCE_INPUTS,
        # The console's schema says Seedance 2.5 makes no drafts; the row follows the API page, which finishes a
        # draft at 1080p only.
        "video": {
            "modes": ALL_MODES,
            "resolutions": ("480p", "720p", "1080p"),
            "durations": (4, 30),
            "can_choose_duration": True,
            "adaptive_modes": ("first_frame", "first_last_frame"),
            "fixed_ratio_modes": (),
            "has_audio": True,
            "has_seed": False,
            "has_fixed_camera": False,
            "output_formats": ("mp4", "mov"),
            "omni_reference_task_types": ("auto", "reference", "edit", "extend"),
            "draft_resolutions": ("1080p",),
        },
        "sources": (*VIDEO_PAGES, "seedance-2-5"),
    },
    "dreamina-seedance-2-0-260128": {
        "kinds": ("videos",),
        "inputs": REFERENCE_INPUTS,
        # ModelArk spells 4K in lowercase.
        "video": {**SERIES_VIDEO, "resolutions": ("480p", "720p", "1080p", "4k")},
        "sources": (*VIDEO_PAGES, "seedance-2-0"),
    },
    "dreamina-seedance-2-0-fast-260128": {
        "kinds": ("videos",),
        "inputs": REFERENCE_INPUTS,
        "video": {**SERIES_VIDEO, "resolutions": ("480p", "720p")},
        "sources": (*VIDEO_PAGES, "seedance-2-0"),
    },
    "dreamina-seedance-2-0-mini-260615": {
        "kinds": ("videos",),
        "inputs": REFERENCE_INPUTS,
        "video": {**SERIES_VIDEO, "resolutions": ("480p", "720p")},
        "sources": (*VIDEO_PAGES, "seedance-2-0"),
    },
    "seedance-1-5-pro-251215": {
        "kinds": ("videos",),
        "inputs": FRAME_INPUTS,
        "video": {
            **PRO_VIDEO,
            "durations": (4, 12),
            "can_choose_duration": True,
            "fixed_ratio_modes": (),
            "has_audio": True,
            "draft_resolutions": ("480p", "720p", "1080p"),
        },
        "sources": (*VIDEO_PAGES, "seedance-1-5-pro", "model-deprecation-notice"),
        "has_flex": True,
        "status": "retiring",
        "deactivation": "2026-11-11",
        "replacement": "dreamina-seedance-2-0-mini-260615",
    },
    "seedance-1-0-pro-250528": {
        "kinds": ("videos",),
        "inputs": FRAME_INPUTS,
        "video": PRO_VIDEO,
        "sources": (*VIDEO_PAGES, "seedance-1-0-pro-pro-fast"),
        "has_flex": True,
    },
    "seedance-1-0-pro-fast-251015": {
        "kinds": ("videos",),
        "inputs": FRAME_INPUTS,
        "video": {**PRO_VIDEO, "modes": ("text", "first_frame")},
        "sources": (*VIDEO_PAGES, "seedance-1-0-pro-pro-fast"),
        "has_flex": True,
    },
}

__all__ = ["VIDEO_ROWS"]
