"""The service tier and extra fields from a Request Options node."""

from . import Json
from dataclasses import dataclass
from collections.abc import Mapping


@dataclass(frozen=True, slots=True)
class Options:
    """The service tier and extra fields to merge into one request.

    Attributes:
        service_tier: The service tier to ask for, "flex", or None for the model's default.
        extra_fields: Top-level request fields added to the body as written.

    """

    service_tier: str | None
    extra_fields: Mapping[str, Json]


__all__ = ["Options"]
