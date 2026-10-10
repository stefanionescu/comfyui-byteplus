"""The parts of BytePlus's replies the extension reads; unknown fields are ignored."""

from . import Reply


class ErrorBody(Reply):
    """One ModelArk error: of a failed reply, a failed task, or a failed image.

    Attributes:
        code: ModelArk's error code, whose parts are separated by dots, such as InvalidParameter.TaskTypeConstraint.
        message: ModelArk's reason.

    """

    code: str | None = None
    message: str = ""


class ErrorReply(Reply):
    """A ModelArk error document.

    Attributes:
        error: The error it describes.

    """

    error: ErrorBody


__all__ = ["ErrorBody", "ErrorReply"]
