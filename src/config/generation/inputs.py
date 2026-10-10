"""Names of the inputs every paid node shares, and of the choice that sends nothing."""

# The inputs every paid node shares.
INPUT_NAMES = {
    "RUN_NUMBER": "run_number",
}

# Every dropdown's choice that sends nothing and leaves the value to the model.
MODEL_DEFAULT = "model default"

__all__ = ["INPUT_NAMES", "MODEL_DEFAULT"]
