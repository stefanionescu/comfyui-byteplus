"""The parts of BytePlus's replies the extension reads; unknown fields are ignored."""

from . import Reply
from pydantic import Field


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


class LayerBoxReply(Reply):
    """Where one layer sits on the base image.

    Attributes:
        absolute: The left, top, right, and bottom edges, in the base image's pixels.

    """

    absolute: tuple[int, int, int, int]


class ImageItemReply(Reply):
    """One image of an image reply: a made image, a layer, or an image refused on its own.

    Attributes:
        url: The image's address, when it was made.
        z_index: A layer's place in the stack; 0 is the base image, and higher layers sit on top.
        bounding_box: Where a layer sits on the base image.
        error: Why this one image was not made, in a series that made others.

    """

    url: str | None = None
    z_index: int = 0
    bounding_box: LayerBoxReply | None = None
    error: ErrorBody | None = None


class ImageReply(Reply):
    """The image endpoint's reply.

    Attributes:
        created: When ModelArk accepted the request, in Unix seconds.
        images: Every image, under ModelArk's name data.
        error: Why no image was made, when none was.

    """

    created: int
    images: tuple[ImageItemReply, ...] = Field(default=(), alias="data")
    error: ErrorBody | None = None


__all__ = ["ErrorBody", "ErrorReply", "ImageItemReply", "ImageReply", "LayerBoxReply"]
