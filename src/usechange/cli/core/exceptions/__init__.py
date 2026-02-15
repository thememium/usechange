"""Exception classes for useChange CLI."""

from __future__ import annotations

from usechange.cli.core.exceptions.base import UsechangeError
from usechange.cli.core.exceptions.config import UsechangeConfigError
from usechange.cli.core.exceptions.usage import UsechangeBadParameter, UsechangeUsageError
from usechange.cli.core.exceptions.validation import UsechangeValidationError

__all__ = [
    "UsechangeError",
    "UsechangeUsageError",
    "UsechangeBadParameter",
    "UsechangeConfigError",
    "UsechangeValidationError",
]
