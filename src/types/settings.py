"""Execution settings and private configuration snapshot records."""

import json
import hashlib
from .credentials import Credential
from dataclasses import field, asdict, dataclass


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

    @property
    def revision(self) -> str:
        """Identify these non-secret settings so a stale window cannot overwrite newer changes."""
        encoded = json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class Configuration:
    """One private settings and API key snapshot for one request.

    Attributes:
        settings: Effective execution limits.
        credential: Private ModelArk API key excluded from representations.
        generation: Token identifying the API key in ComfyUI's cache.

    """

    settings: Settings
    credential: Credential = field(repr=False)
    generation: str


__all__ = ["Configuration", "Settings"]
