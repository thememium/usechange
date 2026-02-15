"""Parameter validation callbacks for strings.

These validators integrate with UsechangeBadParameter for consistent
error styling across the CLI.
"""

from __future__ import annotations

import re

from usechange.cli.core.exceptions import UsechangeBadParameter 


def validate_not_empty(value: str) -> str:
    """Validate that a string value is not empty.

    Args:
        value: The string value to validate.

    Returns:
        The validated value.

    Raises:
        UsechangeBadParameter: If the value is empty or whitespace only.
    """
    if not value or not value.strip():
        raise UsechangeBadParameter("Value cannot be empty", param_hint="value")
    return value


def validate_command_name(value: str) -> str:
    """Validate command name format.

    Command names must:
    - Not be empty
    - Contain only alphanumeric characters, underscores, and hyphens
    - Not start with a number

    Args:
        value: The command name to validate.

    Returns:
        The validated command name.

    Raises:
        UsechangeBadParameter: If the command name is invalid.
    """
    if not value:
        raise UsechangeBadParameter("Command name cannot be empty", param_hint="NAME")

    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_-]*$", value):
        raise UsechangeBadParameter(f"Invalid command name: '{value}'", param_hint="NAME")

    return value
