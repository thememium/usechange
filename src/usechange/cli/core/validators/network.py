"""Parameter validation callbacks for network values."""

from __future__ import annotations

import re

from usechange.cli.core.exceptions import UsechangeBadParameter


def validate_email(value: str) -> str:
    """Validate email address format.

    Args:
        value: The email address to validate.

    Returns:
        The validated email address.

    Raises:
        UsechangeBadParameter: If the email format is invalid.
    """
    if not value:
        raise UsechangeBadParameter("Email cannot be empty", param_hint="--email")

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, value):
        raise UsechangeBadParameter(
            f"Invalid email format: {value}", param_hint="--email"
        )

    return value


def validate_url(value: str) -> str:
    """Validate URL format.

    Args:
        value: The URL to validate.

    Returns:
        The validated URL.

    Raises:
        UsechangeBadParameter: If the URL format is invalid.
    """
    if not value:
        raise UsechangeBadParameter("URL cannot be empty", param_hint="--url")

    pattern = r"^(https?|ftp)://[^\s/$.?#].[^\s]*$"
    if not re.match(pattern, value, re.IGNORECASE):
        raise UsechangeBadParameter(f"Invalid URL format: {value}", param_hint="--url")

    return value


def validate_port(value: str) -> str:
    """Validate network port number.

    Valid port range: 1-65535

    Args:
        value: The port number as string.

    Returns:
        The validated port number.

    Raises:
        UsechangeBadParameter: If the port is invalid.
    """
    try:
        port = int(value)
        if port < 1 or port > 65535:
            raise UsechangeBadParameter(
                f"Port must be between 1 and 65535: {value}",
                param_hint="--port",
            )
    except ValueError:
        raise UsechangeBadParameter(
            f"Port must be a valid integer: {value}", param_hint="--port"
        )

    return value
