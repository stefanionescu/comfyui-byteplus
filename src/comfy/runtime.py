"""Create the shared stores when ComfyUI loads the extension."""

from dataclasses import dataclass

from ..state.errors import ErrorCode, BytePlusError
from ..storage.files import choose_state_directory
from ..config.storage import TASK_FILES
from ..settings.store import ConfigurationStore
from ..byteplus.tasks.records import TaskStore
from ..config.messages.settings import RUNTIME_NOT_READY


@dataclass(frozen=True, slots=True)
class Runtime:
    """State shared by this extension's nodes and routes across event loops.

    Attributes:
        configuration: Private settings and the API key.
        tasks: Recorded video and 3D tasks.

    """

    configuration: ConfigurationStore
    tasks: TaskStore


_runtime: Runtime | None = None


def create_runtime() -> None:
    """Initialize once through the host's extension lifecycle, without network calls.

    The shared stores keep their state under one private directory.
    """
    global _runtime  # noqa: PLW0603 # reason: ComfyUI initializes one shared runtime during loading.
    if _runtime is None:
        configuration = ConfigurationStore(choose_state_directory())
        _runtime = Runtime(configuration, TaskStore(configuration.directory / TASK_FILES['FOLDER']))


def get_runtime() -> Runtime:
    """Reject execution before the host has loaded the extension."""
    if _runtime is None:
        raise BytePlusError(ErrorCode.CONFIGURATION, RUNTIME_NOT_READY)
    return _runtime


__all__ = ['Runtime', 'create_runtime', 'get_runtime']
