"""Error handling utilities for useChange CLI."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.prompt import Confirm

from usechange.cli.config.colors import COLOR
from usechange.cli.core.error.handler import ErrorHandler

console = Console(stderr=True)


def error_exit(message: str, suggestion: str | None = None, code: int = 1) -> None:
    """Display error message and exit with code.

    Convenience function for simple error handling. Displays a styled
    error message and exits immediately with the specified code.

    Args:
        message: Error message to display.
        suggestion: Optional suggestion for fixing the error.
        code: Exit code (default: 1).
    """
    ErrorHandler.display_error(message, suggestion)
    raise typer.Exit(code=code)


def confirm_or_exit(message: str, exit_message: str = "Operation cancelled") -> bool:
    """Prompt for confirmation or exit.

    Uses Rich Confirm.ask with consistent styling. Returns True if user
    confirms, otherwise displays exit message and exits with code 130.

    Args:
        message: Confirmation prompt message.
        exit_message: Message to display if user cancels.

    Returns:
        True if user confirms.

    Raises:
        typer.Exit: With code 130 if user cancels.
    """
    if not Confirm.ask(f"[bold {COLOR.SECONDARY}]{message}[/bold {COLOR.SECONDARY}]"):
        console.print(f"[{COLOR.WARNING}]{exit_message}[/{COLOR.WARNING}]")
        raise typer.Exit(code=130)
    return True
