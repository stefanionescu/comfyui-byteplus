"""The service tier and extra fields from a Request Options node, and the fields every model request shares."""

from dataclasses import dataclass
from collections.abc import Mapping

from . import Json


@dataclass(frozen=True, slots=True)
class Options:
    """The service tier and extra fields to merge into one request.

    Attributes:
        service_tier: The service tier to ask for, `flex`, or None for the model's default.
        extra_fields: Top-level request fields added to the body as written.

    """

    service_tier: str | None
    extra_fields: Mapping[str, Json]


@dataclass(frozen=True, slots=True, kw_only=True)
class ModelRequest:
    """The fields that every request to a ModelArk model shares.

    Attributes:
        model_id: The model ID sent to ModelArk.
        options: The service tier and extra fields from Request Options.

    """

    model_id: str
    options: Options | None


__all__ = ['ModelRequest', 'Options']
