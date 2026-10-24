"""Execution settings and the private configuration records."""

from dataclasses import field, dataclass

from .credentials import Credential


@dataclass(frozen=True, slots=True)
class Settings:
    """Limits that a workflow cannot raise.

    Attributes:
        request_timeout_seconds: How long one request may take; for a video or 3D task, the whole wait.
        max_upload_megabytes: Largest total of encoded media and documents in one request.
        max_download_megabytes: Largest reply body, image, video, last frame, or 3D file accepted.

    """

    request_timeout_seconds: int
    max_upload_megabytes: int
    max_download_megabytes: int


@dataclass(frozen=True, slots=True)
class Configuration:
    """The private settings and API key that one request reads.

    Attributes:
        settings: Effective execution limits.
        credential: Private ModelArk API key excluded from representations.
        generation: Token identifying the API key in ComfyUI's cache.

    """

    settings: Settings
    credential: Credential = field(repr=False)
    generation: str


__all__ = ['Configuration', 'Settings']
