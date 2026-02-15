"""Usage and parameter errors for useChange CLI."""

from __future__ import annotations

import sys
from typing import IO

from click.exceptions import BadParameter, UsageError
from rich.console import Console

from usechange.cli.config.colors import COLOR

console = Console(stderr=True)


class UsechangeUsageError(UsageError):
    """Usage error with styled output and full command help.

    Extends Click's UsageError to provide Rich-styled error messages
    and automatically display command help when an error occurs.
    """

    def show(self, file: IO[str] | None = None) -> None:
        """Display styled usage error with full command help.

        Args:
            file: Optional file to write to (defaults to stderr).
        """
        if file is None:
            file = sys.stderr

        error_prefix = f"[bold {COLOR.ERROR}]ERROR[/bold {COLOR.ERROR}]"
        error_msg = f"[bold {COLOR.ERROR}]{self.format_message()}[/bold {COLOR.ERROR}]"
        console.print(f"{error_prefix}  {error_msg}")

        if self.ctx:
            console.print()
            help_text = self.ctx.get_help()
            console.print(help_text)


class UsechangeBadParameter(BadParameter):
    """Parameter validation error with styled output.

    Use this in parameter callbacks for consistent error styling.
    Provides highlighted error boxes and command help on validation failures.
    """

    def show(self, file: IO[str] | None = None) -> None:
        """Display styled parameter error with command help.

        Args:
            file: Optional file to write to (defaults to stderr).
        """
        if file is None:
            file = sys.stderr

        console.print()

        error_prefix = (
            f"[bold black on {COLOR.ERROR}] ERROR [/bold black on {COLOR.ERROR}]"
        )
        error_msg = f"[bold {COLOR.ERROR}]{self.format_message()}[/bold {COLOR.ERROR}]"
        console.print(f"{error_prefix} {error_msg}")

        if self.ctx:
            help_text = self.ctx.get_help()
            console.print(help_text)
