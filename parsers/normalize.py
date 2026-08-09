"""LLM output normalization — now handled by OutputSchema validators.

This module is retained for backward compatibility.  All normalization
logic has been moved into ``models.contracts.OutputSchema`` via a
``@model_validator(mode='before')`` decorator.

Functions:
    normalize_output: Thin wrapper that delegates to Pydantic validation.
"""

from models.contracts import OutputSchema


def normalize_output(data: dict) -> dict:
    """Normalize LLM output via OutputSchema's built-in validators.

    This is a backward-compatible shim.  New code should call
    ``OutputSchema.model_validate(data)`` directly.

    Args:
        data: The raw parsed JSON dict from the LLM response.

    Returns:
        A normalized dict ready for OutputSchema.

    Raises:
        ValueError: If content is empty, generic, or has insufficient steps.
        pydantic.ValidationError: If the data fails schema validation.
    """
    validated = OutputSchema.model_validate(data)
    return validated.model_dump()
