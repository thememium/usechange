"""Custom exception classes with consistent styling for useChange CLI."""

from __future__ import annotations

from typing import IO

from click.exceptions import ClickException
from rich.console import Console

from usechange.cli.config.colors import COLOR

console = Console(stderr=True)


class UsechangeError(ClickException):
    """Base exception for useChange CLI with Rich styling.

    Provides consistent error styling:
    - ERROR color (#FE686B) for error messages
    - SECONDARY color (#5EFF87) for headers/indicators
    - Suggestions displayed with warning styling

    Attributes:
        exit_code: The exit code to use when this error occurs (default: 1).
        suggestion: Optional suggestion text to display with the error.
    """

    exit_code = 1

    def __init__(self, message: str, suggestion: str | None = None) -> None:
        """Initialize the error with a message and optional suggestion.

        Args:
            message: The error message to display.
            suggestion: Optional suggestion text to help resolve the error.
        """
        super().__init__(message)
        self.suggestion = suggestion

    def show(self, file: IO[str] | None = None) -> None:
        """Display styled error message.

        Args:
            file: Optional file to write to (defaults to stderr).
        """
        error_icon = f"[bold {COLOR.ERROR}]✗[/bold {COLOR.ERROR}]"
        error_msg = f"[bold {COLOR.ERROR}]{self.message}[/bold {COLOR.ERROR}]"

        console.print(f"{error_icon} {error_msg}")

        if self.suggestion:
            suggestion_text = (
                f"[dim {COLOR.WARNING}]💡 {self.suggestion}[/dim {COLOR.WARNING}]"
            )
            console.print(f"  {suggestion_text}")
