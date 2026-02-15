"""Parameter validation callbacks for numeric values."""

from __future__ import annotations

from usechange.cli.core.exceptions import UsechangeBadParameter


def validate_positive_int(value: str) -> str:
    """Validate that a value is a positive integer.

    Args:
        value: The string value to validate.

    Returns:
        The validated value as string.

    Raises:
        UsechangeBadParameter: If the value is not a positive integer.
    """
    try:
        int_value = int(value)
        if int_value <= 0:
            raise UsechangeBadParameter(
                f"Value must be a positive integer: {value}", param_hint="value"
            )
    except ValueError:
        raise UsechangeBadParameter(
            f"Value must be an integer: {value}", param_hint="value"
        )

    return value
