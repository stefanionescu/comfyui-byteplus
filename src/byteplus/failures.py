"""Turn ModelArk's error replies into reviewed messages that carry BytePlus's cleaned reason where it helps."""

import re
from http import HTTPStatus
from collections.abc import Mapping
from pydantic import ValidationError
from ..types.replies import ErrorReply
from ..config.patterns import REASON_PATTERNS
from ..types.errors import ErrorCode, ByteplusError
from ..config.byteplus import CONSOLE_URLS, REASON_ENDINGS, MAX_REASON_CHARACTERS
from ..config.messages.run import (
    NO_REASON,
    REAL_PERSON,
    SERVER_BUSY,
    TASK_FAILED,
    KEY_REJECTED,
    RATE_LIMITED,
    ACCESS_DENIED,
    INPUT_REFUSED,
    LIMIT_REACHED,
    SERVER_FAILED,
    ACCOUNT_STATUS,
    OUTPUT_REFUSED,
    REQUEST_FAILED,
    ACCOUNT_OVERDUE,
    ENDPOINT_CLOSED,
    FREE_QUOTA_USED,
    MODEL_NOT_FOUND,
    TASK_QUEUE_FULL,
    REQUEST_REJECTED,
    MODEL_ID_DISABLED,
    PAYLOAD_TOO_LARGE,
    TASK_TYPE_REFUSED,
    MODEL_NOT_ACTIVATED,
)

_KEY = re.compile(REASON_PATTERNS["KEY"])
_URL = re.compile(REASON_PATTERNS["URL"])
_CONSOLE_URL = re.compile(REASON_PATTERNS["CONSOLE_URL"])
_REQUEST_ID = re.compile(REASON_PATTERNS["REQUEST_ID"])
_FREE_TRIAL = re.compile(REASON_PATTERNS["FREE_TRIAL"])
# ModelArk's codes, each with its category and message. A code that extends a listed one, such as
# InputImageSensitiveContentDetected.PolicyViolation, takes the row of the code it extends.
_FAILURE_CODES: dict[str, tuple[ErrorCode, str]] = {
    "AuthenticationError": (ErrorCode.AUTHENTICATION, KEY_REJECTED),
    "InvalidAccountStatus": (ErrorCode.AUTHENTICATION, ACCOUNT_STATUS),
    "AccessDenied": (ErrorCode.AUTHENTICATION, ACCESS_DENIED),
    "AccountOverdueError": (ErrorCode.CREDITS, ACCOUNT_OVERDUE),
    "OperationDenied.ServiceOverdue": (ErrorCode.CREDITS, ACCOUNT_OVERDUE),
    "ModelNotOpen": (ErrorCode.UNAVAILABLE, MODEL_NOT_ACTIVATED),
    "OperationDenied.ServiceNotOpen": (ErrorCode.UNAVAILABLE, MODEL_NOT_ACTIVATED),
    "InvalidEndpointOrModel.NotFound": (ErrorCode.UNAVAILABLE, MODEL_NOT_FOUND),
    "InvalidEndpointOrModel.ModelIDAccessDisabled": (ErrorCode.UNAVAILABLE, MODEL_ID_DISABLED),
    "InvalidEndpoint.ClosedEndpoint": (ErrorCode.UNAVAILABLE, ENDPOINT_CLOSED),
    "SetLimitExceeded": (ErrorCode.LIMITED, LIMIT_REACHED),
    "QuotaExceeded": (ErrorCode.RATE_LIMITED, TASK_QUEUE_FULL),
    "ServerOverloaded": (ErrorCode.UNAVAILABLE, SERVER_BUSY),
    "RequestBurstTooFast": (ErrorCode.UNAVAILABLE, SERVER_BUSY),
    "ModelAccountRpmRateLimitExceeded": (ErrorCode.RATE_LIMITED, RATE_LIMITED),
    "ModelAccountTpmRateLimitExceeded": (ErrorCode.RATE_LIMITED, RATE_LIMITED),
    "ModelAccountIpmRateLimitExceeded": (ErrorCode.RATE_LIMITED, RATE_LIMITED),
    "ModelAccountFlexTpmRateLimitExceeded": (ErrorCode.RATE_LIMITED, RATE_LIMITED),
    "APIAccountRpmRateLimitExceeded": (ErrorCode.RATE_LIMITED, RATE_LIMITED),
    "AccountRateLimitExceeded": (ErrorCode.RATE_LIMITED, RATE_LIMITED),
    "RateLimitExceeded": (ErrorCode.RATE_LIMITED, RATE_LIMITED),
    "InflightBatchsizeExceeded": (ErrorCode.RATE_LIMITED, RATE_LIMITED),
    "InputImageSensitiveContentDetected.PrivacyInformation": (ErrorCode.REFUSED, REAL_PERSON),
    "InputVideoSensitiveContentDetected.PrivacyInformation": (ErrorCode.REFUSED, REAL_PERSON),
    "SensitiveContentDetected": (ErrorCode.REFUSED, INPUT_REFUSED),
    "InputTextSensitiveContentDetected": (ErrorCode.REFUSED, INPUT_REFUSED),
    "InputImageSensitiveContentDetected": (ErrorCode.REFUSED, INPUT_REFUSED),
    "InputVideoSensitiveContentDetected": (ErrorCode.REFUSED, INPUT_REFUSED),
    "InputAudioSensitiveContentDetected": (ErrorCode.REFUSED, INPUT_REFUSED),
    "OutputTextSensitiveContentDetected": (ErrorCode.REFUSED, OUTPUT_REFUSED),
    "OutputImageSensitiveContentDetected": (ErrorCode.REFUSED, OUTPUT_REFUSED),
    "OutputVideoSensitiveContentDetected": (ErrorCode.REFUSED, OUTPUT_REFUSED),
    "OutputAudioSensitiveContentDetected": (ErrorCode.REFUSED, OUTPUT_REFUSED),
    "InvalidParameter.TaskTypeConstraint": (ErrorCode.INVALID_INPUT, TASK_TYPE_REFUSED),
    "InvalidParameter.TaskTypeMismatch": (ErrorCode.INVALID_INPUT, TASK_TYPE_REFUSED),
    "InvalidParameter": (ErrorCode.INVALID_INPUT, REQUEST_REJECTED),
    "MissingParameter": (ErrorCode.INVALID_INPUT, REQUEST_REJECTED),
    "InvalidArgumentError": (ErrorCode.INVALID_INPUT, REQUEST_REJECTED),
    "InvalidImageURL": (ErrorCode.INVALID_INPUT, REQUEST_REJECTED),
    "OutofContextError": (ErrorCode.INVALID_INPUT, REQUEST_REJECTED),
    "InternalServiceError": (ErrorCode.TRANSPORT, SERVER_FAILED),
}
# QuotaExceeded is the one code whose meaning only ModelArk's wording tells apart: a used-up free trial needs the
# model activated, while the other replies need fewer queued tasks.
_FREE_TRIAL_CODES: dict[str, tuple[ErrorCode, str]] = {"QuotaExceeded": (ErrorCode.LIMITED, FREE_QUOTA_USED)}
# The statuses that decide a failure whose code is missing or unknown.
_STATUS_FAILURES: dict[int, tuple[ErrorCode, str]] = {
    401: (ErrorCode.AUTHENTICATION, KEY_REJECTED),
    403: (ErrorCode.AUTHENTICATION, ACCESS_DENIED),
    404: (ErrorCode.UNAVAILABLE, MODEL_NOT_FOUND),
    413: (ErrorCode.INVALID_INPUT, PAYLOAD_TOO_LARGE),
    429: (ErrorCode.RATE_LIMITED, RATE_LIMITED),
}


def _find_failure(code: str, failures: Mapping[str, tuple[ErrorCode, str]]) -> tuple[ErrorCode, str] | None:
    """Look a code up whole, then without its last dot-separated part, until a part is listed or nothing is left.

    Some codes end in a dot, such as InvalidParameter., so the empty last part is dropped like any other.
    """
    candidate = code
    while candidate:
        if candidate in failures:
            return failures[candidate]
        candidate = candidate.rpartition(".")[0]
    return None


def _choose_status_failure(status: int | None) -> tuple[ErrorCode, str]:
    """Choose the category and message of a status when the code names none.

    A failed task has no status. An error inside a successful reply, such as one failed image, is a refused request.
    A redirect is never followed, so it is an unexpected reply.
    """
    if status is None:
        return ErrorCode.UNAVAILABLE, TASK_FAILED
    if status in _STATUS_FAILURES:
        return _STATUS_FAILURES[status]
    is_success = HTTPStatus.OK <= status < HTTPStatus.MULTIPLE_CHOICES
    if is_success or HTTPStatus.BAD_REQUEST <= status < HTTPStatus.INTERNAL_SERVER_ERROR:
        return ErrorCode.INVALID_INPUT, REQUEST_REJECTED
    return ErrorCode.TRANSPORT, SERVER_FAILED if status >= HTTPStatus.INTERNAL_SERVER_ERROR else REQUEST_FAILED


def _choose_failure(status: int | None, code: str | None, message: str) -> tuple[ErrorCode, str]:
    """Choose by code, the free trial wording first, then by status for a code that is missing or unknown."""
    if code:
        tables = (_FREE_TRIAL_CODES, _FAILURE_CODES) if _FREE_TRIAL.search(message) else (_FAILURE_CODES,)
        for failures in tables:
            failure = _find_failure(code, failures)
            if failure is not None:
                return failure
    return _choose_status_failure(status)


def _sanitize_reason(message: str) -> str:
    """Remove the only private details a reason can carry, then shorten it.

    Console addresses stay, without the scheme. Other addresses go, since storage links carry signatures, and so do
    ModelArk's request ID and key-shaped text. The reason ends as a sentence, since a message may add its next step
    after it.
    """
    text = _URL.sub("", _CONSOLE_URL.sub(r"\1", message))
    text = " ".join(_KEY.sub("", _REQUEST_ID.sub("", text)).split())
    if len(text) > MAX_REASON_CHARACTERS:
        text = text[: MAX_REASON_CHARACTERS - 1].rstrip() + "…"
    if text and not text.endswith(REASON_ENDINGS):
        text += "."
    return text or NO_REASON


def build_failure(status: int | None, code: str | None, message: str) -> ByteplusError:
    """Build the reviewed error for one ModelArk error, by its code and then its status, with the cleaned reason.

    The status is None for the error of a failed task, and the reply's status for an error inside a successful reply.
    A message without a reason placeholder drops the reason.
    """
    category, template = _choose_failure(status, code, message)
    text = template.format(reason=_sanitize_reason(message), status=status, **CONSOLE_URLS)
    return ByteplusError(category, text)


def read_failure(status: int, body: bytes) -> ByteplusError:
    """Read a failed reply's error document; a body that is not one gives no code and no reason."""
    try:
        error = ErrorReply.model_validate_json(body).error
    except ValidationError:
        return build_failure(status, None, "")
    return build_failure(status, error.code, error.message)


__all__ = ["build_failure", "read_failure"]
