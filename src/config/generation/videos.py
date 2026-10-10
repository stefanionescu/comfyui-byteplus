"""Video choices, limits, and the task timing that video and 3D share."""

from .inputs import MODEL_DEFAULT

# The duration widget's default and largest value, and what 0 is sent as: -1, which lets the model choose.
DURATION = {
    "DEFAULT": 5,
    "MAX": 30,
    "AUTO": -1,
}

# The resolution widget's choices and default, and the size every draft is made at.
RESOLUTIONS = {
    "CHOICES": ("480p", "720p", "1080p", "4k"),
    "DEFAULT": "720p",
    "DRAFT": "480p",
}

# Every Seedance model takes every one of these ratios, so the model rows do not list them.
ASPECT_RATIOS = (MODEL_DEFAULT, "adaptive", "16:9", "4:3", "1:1", "3:4", "9:16", "21:9")

# The ratio sent where a model keeps the shape of its input.
ADAPTIVE_RATIO = "adaptive"

# Whether the video has sound.
AUDIO_CHOICES = (MODEL_DEFAULT, "on", "off")

# What Seedance 2.5 does with reference media; auto sends nothing and lets the model decide.
TASK_TYPES = ("auto", "reference", "edit", "extend")

# The task types that keep the shape of the reference video, so they take only the adaptive ratio.
ADAPTIVE_TASK_TYPES = ("edit", "extend")

# The video file formats.
OUTPUT_FORMATS = (MODEL_DEFAULT, "mp4", "mov")

# A local frame or reference image every Seedance model reads: each side in pixels, and width over height.
IMAGE_BOUNDS = {
    "MIN_SIDE": 300,
    "MAX_SIDE": 6000,
    "MIN_ASPECT": 0.4,
    "MAX_ASPECT": 2.5,
}

# The time between a video task's status checks; the first check is immediate.
POLL_INTERVAL_SECONDS = 10

# ModelArk answers status checks for 7 days after a task was created.
TASK_RETENTION_SECONDS = 604_800

# The statuses of a task that has ended.
DONE_STATUSES = ("succeeded", "failed", "cancelled", "expired")

# The one status ModelArk can cancel; a task that started runs to the end.
CANCELLABLE_STATUS = "queued"

# The output addresses a finished task may hold, in download order: a video, its last frame, and a 3D file.
CONTENT_FIELDS = ("video_url", "last_frame_url", "file_url")

# A Download node lists each recorded task as its ID, model, and submit time, joined by this separator.
JOB_LABEL_SEPARATOR = " · "

# The submit time to the minute, the first 16 characters of the ISO time.
JOB_TIME_CHARACTERS = 16

__all__ = [
    "ADAPTIVE_RATIO",
    "ADAPTIVE_TASK_TYPES",
    "ASPECT_RATIOS",
    "AUDIO_CHOICES",
    "CANCELLABLE_STATUS",
    "CONTENT_FIELDS",
    "DONE_STATUSES",
    "DURATION",
    "IMAGE_BOUNDS",
    "JOB_LABEL_SEPARATOR",
    "JOB_TIME_CHARACTERS",
    "OUTPUT_FORMATS",
    "POLL_INTERVAL_SECONDS",
    "RESOLUTIONS",
    "TASK_RETENTION_SECONDS",
    "TASK_TYPES",
]
