"""Messages for video and 3D tasks: recording, waiting, cancelling, and collecting them.

{seconds} is the request timeout in BytePlus settings.
"""

JOB_UNKNOWN = "Choose an unfinished task from the list. Press R in ComfyUI to refresh the list."

MESH_CANCELLED = (
    "The 3D task was cancelled before it started, so nothing was billed. Run 3D: Generate again to start a new task."
)

MESH_EXPIRED = (
    "The 3D task ran out of time before it finished, so ModelArk stopped it without billing. Run 3D: Generate again "
    "to start a new task."
)

MESH_JOB_KIND = "That task is a video. Collect it with Video: Download."

MESH_NOT_GLB = (
    "ModelArk returned a file that is not a GLB model, so ComfyUI cannot open it. The task finished and may be "
    "billed; check Usage in the ModelArk console before running again."
)

MESH_WAIT_LIMIT = (
    "The 3D model was not ready within the request timeout of {seconds} seconds in BytePlus settings. ModelArk keeps "
    "making it; collect it with 3D: Download."
)

TASK_FILES_EXPIRED = (
    "This task finished more than 24 hours ago, and ModelArk deletes its files after 24 hours, so they can no longer "
    "be downloaded."
)

TASK_GONE = "ModelArk keeps tasks for 7 days, and this one is older. Run the node again to start a new task."

TASK_UNRECORDED = (
    "ModelArk accepted the task, but its reply could not be read, so the task was not recorded. It may be running "
    "and billed; check Usage in the ModelArk console before running again."
)

VIDEO_CANCELLED = (
    "The video task was cancelled before it started, so nothing was billed. Run the node again to start a new task."
)

VIDEO_EXPIRED = (
    "The video task ran out of time before it finished, so ModelArk stopped it without billing. Run the node again "
    "to start a new task."
)

VIDEO_JOB_KIND = "That task is a 3D model. Collect it with 3D: Download."

VIDEO_WAIT_LIMIT = (
    "The video was not ready within the request timeout of {seconds} seconds in BytePlus settings. ModelArk keeps "
    "making it; collect it with Video: Download."
)

# The end of a wait that is not a success or a failure, for each kind of task.
TASK_OUTCOMES = {
    "videos": {
        "WAIT_LIMIT": VIDEO_WAIT_LIMIT,
        "CANCELLED": VIDEO_CANCELLED,
        "EXPIRED": VIDEO_EXPIRED,
    },
    "meshes": {
        "WAIT_LIMIT": MESH_WAIT_LIMIT,
        "CANCELLED": MESH_CANCELLED,
        "EXPIRED": MESH_EXPIRED,
    },
}

__all__ = [
    "JOB_UNKNOWN",
    "MESH_CANCELLED",
    "MESH_EXPIRED",
    "MESH_JOB_KIND",
    "MESH_NOT_GLB",
    "MESH_WAIT_LIMIT",
    "TASK_FILES_EXPIRED",
    "TASK_GONE",
    "TASK_OUTCOMES",
    "TASK_UNRECORDED",
    "VIDEO_CANCELLED",
    "VIDEO_EXPIRED",
    "VIDEO_JOB_KIND",
    "VIDEO_WAIT_LIMIT",
]
