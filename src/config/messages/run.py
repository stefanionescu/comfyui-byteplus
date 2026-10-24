"""Messages for ModelArk failures.

{reason} is ModelArk's cleaned reason, ending as a sentence. Console placeholders are filled from CONSOLE_URLS.
"""

ACCESS_DENIED = (
    "ModelArk refused this API key: {reason} Check the key's model permissions, project, and IP allowlist at "
    "{key_page}."
)

ACCOUNT_OVERDUE = (
    "Your BytePlus account has an overdue balance, so ModelArk refuses requests. Top up at {billing_page}, then run "
    "again."
)

ACCOUNT_STATUS = (
    "BytePlus reports a problem with your account's status. Check the account in the BytePlus console, or contact "
    "BytePlus support."
)

ANSWER_CUT = (
    "The model reached its token limit before it began the answer. Raise max_completion_tokens or set it to 0, or "
    "lower reasoning_effort or set thinking to disabled."
)

ANSWER_FILTERED = "ModelArk's content moderation stopped the answer. Change the prompt or the media, and run again."

BYTEPLUS_UNREACHABLE = "ComfyUI could not reach BytePlus. Check the connection and try again."

ENDPOINT_CLOSED = "ModelArk's endpoint for this model is closed or briefly unavailable. Try again later."

FREE_QUOTA_USED = (
    "This model's free trial quota is used up, and the model is not activated. Activate it at {activation_page} to "
    "keep using it with paid billing."
)

INPUT_REFUSED = "ModelArk's content check refused an input: {reason} Change the prompt or the media, then run again."

KEY_REJECTED = (
    "ModelArk did not accept the API key. Check the key in BytePlus Settings, and that it was made in the Asia "
    "Pacific (Johor) region."
)

LIMIT_REACHED = (
    "ModelArk paused this model because your account reached a limit set on it: its model usage limit, or Free "
    "Credits Only mode. Raise or close the limit at {activation_page}, then run again."
)

MODEL_ID_DISABLED = (
    "Your BytePlus account is set to call models only through endpoint IDs, which this extension does not support. "
    "Contact BytePlus support, or use an account that can call model IDs."
)

MODEL_NOT_ACTIVATED = (
    "This model is not activated on your BytePlus account. Activate it at {activation_page}, then run again."
)

MODEL_NOT_FOUND = (
    "ModelArk has no model by this ID that the API key may use: {reason} Check the ID, and the key's model "
    "permissions at {key_page}."
)

NO_REASON = "no reason given."

OUTPUT_DOWNLOAD_FAILED = (
    "The output file could not be downloaded from BytePlus storage: HTTP {status}. Output addresses last 24 hours. "
    "A video or 3D task stays recorded, so its Download node can collect it again."
)

OUTPUT_REFUSED = (
    "ModelArk's content check withheld what the model made: {reason} Change the prompt or the media, then run again."
)

PAYLOAD_TOO_LARGE = "The request is larger than the 64 MB ModelArk accepts. Send fewer or smaller files."

RATE_LIMITED = "ModelArk is limiting requests: {reason} Wait a moment before running again."

REAL_PERSON = (
    "ModelArk refused a reference that may show a real person. Use a preset character or an asset through Reference: "
    "Add, or pass a ModelArk output on unchanged from the references output of the node that made it."
)

REPLY_EMPTY = "ModelArk's reply held no result. Run again or choose another model."

REPLY_UNREADABLE = (
    "ModelArk's reply could not be read. The request may still have run; check the Usage page in the ModelArk "
    "console before running again."
)

REQUEST_FAILED = "ModelArk returned HTTP {status}. Try again later."

REQUEST_REJECTED = "ModelArk refused the request: {reason}"

REQUEST_TIMEOUT = (
    "The request took longer than {seconds} seconds, the Request timeout (seconds) in BytePlus Settings. It may "
    "still have run and been billed; check the Usage page at {usage_page} before running again."
)

REQUEST_UNCERTAIN = (
    "The connection closed before ModelArk answered. It may have run and billed this request; check the Usage page "
    "at {usage_page} before running again."
)

SERVER_BUSY = (
    "ModelArk is overloaded, or your requests rose too fast. Wait a few minutes, then run again with fewer requests "
    "at once."
)

SERVER_FAILED = "ModelArk failed with an internal error: {reason} Try again later."

TASK_FAILED = "ModelArk could not finish the task: {reason}"

TASK_QUEUE_FULL = (
    "ModelArk has too many of your tasks waiting: {reason} Wait for queued video or 3D tasks to finish, then run again."
)

TASK_TYPE_REFUSED = (
    "Seedance read the inputs as a different kind of video task than the request allows: {reason} Change the "
    "references, the prompt, or omni_reference_task_type, then run again."
)

__all__ = [
    "ACCESS_DENIED",
    "ACCOUNT_OVERDUE",
    "ACCOUNT_STATUS",
    "ANSWER_CUT",
    "ANSWER_FILTERED",
    "BYTEPLUS_UNREACHABLE",
    "ENDPOINT_CLOSED",
    "FREE_QUOTA_USED",
    "INPUT_REFUSED",
    "KEY_REJECTED",
    "LIMIT_REACHED",
    "MODEL_ID_DISABLED",
    "MODEL_NOT_ACTIVATED",
    "MODEL_NOT_FOUND",
    "NO_REASON",
    "OUTPUT_DOWNLOAD_FAILED",
    "OUTPUT_REFUSED",
    "PAYLOAD_TOO_LARGE",
    "RATE_LIMITED",
    "REAL_PERSON",
    "REPLY_EMPTY",
    "REPLY_UNREADABLE",
    "REQUEST_FAILED",
    "REQUEST_REJECTED",
    "REQUEST_TIMEOUT",
    "REQUEST_UNCERTAIN",
    "SERVER_BUSY",
    "SERVER_FAILED",
    "TASK_FAILED",
    "TASK_QUEUE_FULL",
    "TASK_TYPE_REFUSED",
]
