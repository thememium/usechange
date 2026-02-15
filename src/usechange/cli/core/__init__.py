"""Core CLI utilities for useChange.

This module provides core functionality for the usechange CLI including:
- Color constants and styling
- Custom exception classes with Rich formatting
- Centralized error handling
- Parameter validators
"""

from __future__ import annotations

import sys
from importlib import import_module

from usechange.cli.config.colors import COLOR
from usechange.cli.core.error import ErrorHandler, confirm_or_exit, error_exit
from usechange.cli.core.exceptions import (
    UsechangeBadParameter,
    UsechangeConfigError,
    UsechangeError,
    UsechangeUsageError,
    UsechangeValidationError,
)
from usechange.cli.core.validators import (
    validate_command_name,
    validate_directory_exists,
    validate_email,
    validate_file_exists,
    validate_not_empty,
    validate_path_exists,
    validate_port,
    validate_positive_int,
    validate_url,
)

sys.modules.setdefault(__name__ + ".colors", import_module("usechange.cli.config.colors"))
sys.modules.setdefault(__name__ + ".list", import_module("usechange.cli.core.ui.list"))
sys.modules.setdefault(__name__ + ".title", import_module("usechange.cli.core.ui.title"))
sys.modules.setdefault(
    __name__ + ".error_handler", import_module("usechange.cli.core.error.handler")
)

__all__ = [
    # Colors
    "COLOR",
    # Exceptions
    "UsechangeError",
    "UsechangeUsageError",
    "UsechangeBadParameter",
    "UsechangeConfigError",
    "UsechangeValidationError",
    # Error handling
    "ErrorHandler",
    "error_exit",
    "confirm_or_exit",
    # Validators
    "validate_not_empty",
    "validate_command_name",
    "validate_path_exists",
    "validate_file_exists",
    "validate_directory_exists",
    "validate_email",
    "validate_url",
    "validate_positive_int",
    "validate_port",
]
