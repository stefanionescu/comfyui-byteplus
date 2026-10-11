"""Messages for video and 3D tasks: recording, waiting, cancelling, and collecting them.

{task} is the kind of task in the words of TASK_NAMES, {node} is the node that starts it or collects it, and {seconds}
is the Request timeout (seconds) in BytePlus Settings.
"""

TASK_UNKNOWN = "Choose an unfinished task from the list. Press R in ComfyUI to refresh the list."

MESH_NOT_GLB = (
    "ModelArk returned a file that is not a GLB model, so ComfyUI cannot open it. The task finished and may be "
    "billed; check the Usage page in the ModelArk console before running again."
)

TASK_CANCELLED = (
    "The {task} task was cancelled before it started, so nothing was billed. Run {node} again to start a new task."
)

TASK_EXPIRED = (
    "The {task} task ran out of time before it finished, so ModelArk stopped it without billing. Run {node} again "
    "to start a new task."
)

TASK_FILES_EXPIRED = (
    "This task finished more than 24 hours ago, and ModelArk deletes its files after 24 hours, so they can no longer "
    "be downloaded."
)

TASK_GONE = "ModelArk keeps tasks for 7 days, and this one is older. Run {node} again to start a new task."

TASK_KIND = "That task is a {task} task. Collect it with {node}."

TASK_UNRECORDED = (
    "ModelArk accepted the task, but its reply could not be read, so the task was not recorded. It may be running "
    "and billed; check the Usage page in the ModelArk console before running again."
)

TASK_WAIT_LIMIT = (
    "The {task} task was not ready within {seconds} seconds, the Request timeout (seconds) in BytePlus Settings. "
    "ModelArk keeps running it; collect it with {node}."
)

# Each kind of task as {task} names it, and the node that collects it.
TASK_NAMES = {"videos": "video", "meshes": "3D"}
DOWNLOAD_NODES = {"videos": "Video: Download", "meshes": "3D: Download"}

__all__ = [
    "DOWNLOAD_NODES",
    "MESH_NOT_GLB",
    "TASK_CANCELLED",
    "TASK_EXPIRED",
    "TASK_FILES_EXPIRED",
    "TASK_GONE",
    "TASK_KIND",
    "TASK_NAMES",
    "TASK_UNKNOWN",
    "TASK_UNRECORDED",
    "TASK_WAIT_LIMIT",
]
