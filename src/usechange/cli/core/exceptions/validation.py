"""Validation errors with severity levels for useChange CLI."""

from __future__ import annotations

from typing import IO

from rich.console import Console

from usechange.cli.config.colors import COLOR
from usechange.cli.core.exceptions.base import UsechangeError

console = Console(stderr=True)


class UsechangeValidationError(UsechangeError):
    """Validation errors with severity levels.

    Supports warning, error, and critical severity levels with
    appropriate styling and exit codes.

    Attributes:
        SEVERITY_STYLES: Mapping of severity levels to their styles.
        severity: The severity level of the error.
        icon: The icon to display based on severity.
        color: The color to use based on severity.
    """

    SEVERITY_STYLES: dict[str, dict[str, str]] = {
        "warning": {"color": COLOR.WARNING, "icon": "⚠"},
        "error": {"color": COLOR.ERROR, "icon": "✗"},
        "critical": {"color": COLOR.ERROR, "icon": "☠"},
    }

    def __init__(
        self,
        message: str,
        severity: str = "error",
        suggestion: str | None = None,
    ) -> None:
        """Initialize the validation error.

        Args:
            message: The error message to display.
            severity: The severity level (warning, error, or critical).
            suggestion: Optional suggestion text to help resolve the error.
        """
        super().__init__(message, suggestion)
        self.severity = severity
        style = self.SEVERITY_STYLES.get(severity, self.SEVERITY_STYLES["error"])
        self.icon = style["icon"]
        self.color = style["color"]
        self.exit_code = 1 if severity in ("error", "critical") else 0

    def show(self, file: IO[str] | None = None) -> None:
        """Display validation error with severity styling.

        Args:
            file: Optional file to write to (defaults to stderr).
        """
        icon = f"[bold {self.color}]{self.icon}[/bold {self.color}]"
        msg = f"[bold {self.color}]{self.message}[/bold {self.color}]"

        console.print(f"{icon} {msg}")

        if self.suggestion:
            suggestion_text = (
                f"[dim {COLOR.WARNING}]💡 {self.suggestion}[/dim {COLOR.WARNING}]"
            )
            console.print(f"  {suggestion_text}")
