"""Configuration-related errors for useChange CLI."""

from __future__ import annotations

from typing import IO

from rich.console import Console

from usechange.cli.config.colors import COLOR
from usechange.cli.core.exceptions.base import UsechangeError 

console = Console(stderr=True)


class UsechangeConfigError(UsechangeError):
    """Configuration-related errors with file context.

    Attributes:
        config_file: Path to the configuration file that caused the error.
    """

    def __init__(
        self,
        message: str,
        config_file: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        """Initialize the configuration error.

        Args:
            message: The error message to display.
            config_file: Optional path to the configuration file.
            suggestion: Optional suggestion text to help resolve the error.
        """
        super().__init__(message, suggestion)
        self.config_file = config_file

    def show(self, file: IO[str] | None = None) -> None:
        """Display configuration error with file context.

        Args:
            file: Optional file to write to (defaults to stderr).
        """
        console.rule(
            title=f"[bold {COLOR.ERROR}]Configuration Error[/bold {COLOR.ERROR}]",
            style=COLOR.ERROR,
            align="left",
        )

        if self.config_file:
            console.print(
                f"[{COLOR.FOREGROUND_MUTED}]File: {self.config_file}[/{COLOR.FOREGROUND_MUTED}]"
            )
            console.print()

        error_msg = f"[bold {COLOR.ERROR}]{self.message}[/bold {COLOR.ERROR}]"
        console.print(error_msg)

        if self.suggestion:
            suggestion_text = (
                f"[dim {COLOR.WARNING}]💡 {self.suggestion}[/dim {COLOR.WARNING}]"
            )
            console.print(f"  {suggestion_text}")
