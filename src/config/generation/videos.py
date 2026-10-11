"""Video choices, limits, and the task timing that video and 3D share."""

from .inputs import MODEL_DEFAULT

# The duration widget's default and largest value, and -1, which lets the model choose.
DURATION = {
    "DEFAULT": 5,
    "MAX": 30,
    "AUTO": -1,
}

# The resolution widget's choices and default.
RESOLUTION_CHOICES = ("480p", "720p", "1080p", "4k")
RESOLUTION_DEFAULT = "720p"

# The resolution every draft is made at.
DRAFT_RESOLUTION = "480p"

# The seed widget's default and largest value, in Seedance's range.
SEED = {
    "DEFAULT": 42,
    "MAX": 2**31 - 1,
}

# Every Seedance model takes every one of these ratios, so the model rows do not list them.
RATIOS = (MODEL_DEFAULT, "adaptive", "16:9", "4:3", "1:1", "3:4", "9:16", "21:9")

# The ratio sent where a model keeps the shape of its input.
ADAPTIVE_RATIO = "adaptive"

# The generate_audio choices; the boolean each sends.
AUDIO_CHOICES = (MODEL_DEFAULT, "true", "false")
AUDIO_VALUES = {"true": True, "false": False}

# The omni_reference_task_type values: what Seedance 2.5 does with reference media. auto, ModelArk's default, sends
# nothing and lets the model decide.
TASK_TYPES = ("auto", "reference", "edit", "extend")

# The task types that keep the shape of the reference video, so they take only the adaptive ratio.
ADAPTIVE_TASK_TYPES = ("edit", "extend")

# The output_format choices.
OUTPUT_FORMATS = (MODEL_DEFAULT, "mp4", "mov")

# The time between a video or 3D task's status checks; the first check is immediate.
POLL_INTERVAL_SECONDS = 10

# ModelArk answers status checks for 7 days after a task was created.
TASK_RETENTION_SECONDS = 604_800

# The statuses of a task that has ended.
DONE_STATUSES = ("succeeded", "failed", "cancelled", "expired")

# The one status ModelArk can cancel; a task that started runs to the end.
CANCELLABLE_STATUS = "queued"

# A Download node lists each recorded task as its ID, model, and submit time, joined by this separator.
JOB_LABEL_SEPARATOR = " · "

# The submit time to the minute, the first 16 characters of the ISO time.
JOB_TIME_CHARACTERS = 16

__all__ = [
    "ADAPTIVE_RATIO",
    "ADAPTIVE_TASK_TYPES",
    "AUDIO_CHOICES",
    "AUDIO_VALUES",
    "CANCELLABLE_STATUS",
    "DONE_STATUSES",
    "DRAFT_RESOLUTION",
    "DURATION",
    "JOB_LABEL_SEPARATOR",
    "JOB_TIME_CHARACTERS",
    "OUTPUT_FORMATS",
    "POLL_INTERVAL_SECONDS",
    "RATIOS",
    "RESOLUTION_CHOICES",
    "RESOLUTION_DEFAULT",
    "SEED",
    "TASK_RETENTION_SECONDS",
    "TASK_TYPES",
]
