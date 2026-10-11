"""Create the shared stores when ComfyUI loads the extension."""

from ..config.storage import TASK_FILES
from ..byteplus.tasks.records import TaskStore
from ..settings.store import ConfigurationStore
from ..storage.files import choose_state_directory
from ..types.errors import ErrorCode, BytePlusError
from ..config.messages.settings import RUNTIME_NOT_READY


class Runtime:
    """State shared by this extension's nodes and routes across event loops.

    Attributes:
        configuration: Private settings and the API key.
        tasks: Recorded video and 3D tasks.

    """

    __slots__ = ("configuration", "tasks")

    configuration: ConfigurationStore
    tasks: TaskStore

    def __init__(self) -> None:
        """Create the shared stores and place their state under one private directory."""
        self.configuration = ConfigurationStore(choose_state_directory())
        self.tasks = TaskStore(self.configuration.directory / TASK_FILES["FOLDER"])


_runtime: Runtime | None = None


def create_runtime() -> None:
    """Initialize once through the host's extension lifecycle, without network calls."""
    global _runtime  # noqa: PLW0603 -- reason: ComfyUI initializes one shared runtime during loading.
    if _runtime is None:
        _runtime = Runtime()


def get_runtime() -> Runtime:
    """Reject execution before the host has loaded the extension."""
    if _runtime is None:
        raise BytePlusError(ErrorCode.CONFIGURATION, RUNTIME_NOT_READY)
    return _runtime


__all__ = ["Runtime", "create_runtime", "get_runtime"]
