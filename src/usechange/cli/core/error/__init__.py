"""Error handling utilities for usechange CLI."""

from __future__ import annotations

from usechange.cli.core.error.handler import ErrorHandler
from usechange.cli.core.error.utils import confirm_or_exit, error_exit

__all__ = [
    "ErrorHandler",
    "error_exit",
    "confirm_or_exit",
]
