"""Errors that the extension can show without exposing provider data."""

from enum import StrEnum


class ErrorCode(StrEnum):
    """Stable categories for the messages a person reads."""

    CONFIGURATION = 'configuration'
    AUTHENTICATION = 'authentication'
    CREDITS = 'credits'
    INVALID_INPUT = 'invalid_input'
    REFUSED = 'refused'
    UNAVAILABLE = 'unavailable'
    RATE_LIMITED = 'rate_limited'
    # A model usage limit, Free Credits Only mode, or a used-up free quota; waiting does not lift it.
    LIMITED = 'limited'
    TIMEOUT = 'timeout'
    TRANSPORT = 'transport'
    UNCERTAIN = 'uncertain'
    INTERRUPTED = 'interrupted'
    CONFLICT = 'conflict'
    MEDIA = 'media'


class BytePlusError(RuntimeError):
    """Show reviewed text; ModelArk's cleaned reason, when there is one, is already part of it."""

    def __init__(self, code: ErrorCode, message: str) -> None:
        """Store the complete message and its category."""
        super().__init__(message)
        self.code = code


class UnknownModelError(BytePlusError):
    """A model ID the bundled table does not know, which ModelArk's model listing may still list."""


__all__ = ['BytePlusError', 'ErrorCode', 'UnknownModelError']
