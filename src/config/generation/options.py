"""The choices of Request Options."""

from .inputs import MODEL_DEFAULT

# The service_tier dropdown: nothing sent, or ModelArk's lower-priority, lower-cost tier.
TIER_CHOICES = (MODEL_DEFAULT, "flex")

__all__ = ["TIER_CHOICES"]
