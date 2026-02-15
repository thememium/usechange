"""Centralized error handling for useChange CLI.

Provides consistent error styling and formatting across the application,
matching your existing help and fzf command styling.
"""

from __future__ import annotations

import functools
from typing import Callable, TypeVar

import typer
from rich.console import Console

from usechange.cli.config.colors import COLOR
from usechange.cli.core.exceptions import UsechangeError

console = Console(stderr=True)

F = TypeVar("F", bound=Callable[..., object])


class ErrorHandler:
    """Centralized error handling with consistent styling."""

    @staticmethod
    def display_error(message: str, suggestion: str | None = None) -> None:
        """Display a styled error message.

        Matches your existing error styling pattern:
        - Red ✗ icon
        - Bold red message
        - Optional yellow suggestion

        Args:
            message: Error message to display.
            suggestion: Optional suggestion for fixing the error.
        """
        error_icon = f"[bold {COLOR.ERROR}]✗[/bold {COLOR.ERROR}]"
        error_msg = f"[bold {COLOR.ERROR}]{message}[/bold {COLOR.ERROR}]"

        console.print(f"{error_icon} {error_msg}")

        if suggestion:
            suggestion_text = (
                f"[dim {COLOR.WARNING}]💡 {suggestion}[/dim {COLOR.WARNING}]"
            )
            console.print(f"  {suggestion_text}")

    @staticmethod
    def display_warning(message: str, suggestion: str | None = None) -> None:
        """Display a styled warning message.

        Uses your WARNING color (#F5FE53).

        Args:
            message: Warning message to display.
            suggestion: Optional suggestion or additional info.
        """
        warning_icon = f"[bold {COLOR.WARNING}]⚠[/bold {COLOR.WARNING}]"
        warning_msg = f"[bold {COLOR.WARNING}]{message}[/bold {COLOR.WARNING}]"

        console.print()
        console.print(f"{warning_icon} {warning_msg}")

        if suggestion:
            suggestion_text = f"[dim {COLOR.INFO}]💡 {suggestion}[/dim {COLOR.INFO}]"
            console.print(f"  {suggestion_text}")

    @staticmethod
    def display_success(message: str) -> None:
        """Display a styled success message.

        Uses your SUCCESS color (#5EFF87).

        Args:
            message: Success message to display.
        """
        success_icon = f"[bold {COLOR.SUCCESS}]✓[/bold {COLOR.SUCCESS}]"
        success_msg = f"[bold {COLOR.SUCCESS}]{message}[/bold {COLOR.SUCCESS}]"

        console.print(f"{success_icon} {success_msg}")

    @staticmethod
    def handle_exception(func: F) -> F:
        """Decorator to handle exceptions with consistent styling.

        Catches UsechangeError and general exceptions, displaying them
        with consistent styling before exiting.

        Usage:
            @ErrorHandler.handle_exception
            def my_command():
                raise UsechangeError("Something went wrong")

        Args:
            func: Function to decorate.

        Returns:
            Decorated function with exception handling.
        """

        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            try:
                return func(*args, **kwargs)
            except UsechangeError as e:
                e.show()
                raise typer.Exit(code=e.exit_code)
            except Exception as e:
                ErrorHandler.display_error(
                    f"Unexpected error: {e!s}",
                    suggestion="Run with --verbose for more details",
                )
                raise typer.Exit(code=1)

        return wrapper  # type: ignore[return-value]
