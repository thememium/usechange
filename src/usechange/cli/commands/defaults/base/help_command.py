"""Help command for displaying CLI help information."""

from __future__ import annotations

from usechange.cli.core.base_command import BaseCommand
from usechange.cli.core.ui.list import list_commands


class HelpCommand(BaseCommand):
    """Command for displaying help information."""

    def signature(self) -> str:
        """Return the command signature."""
        return "help"

    def description(self) -> str:
        """Return the command description."""
        return "Show help information"

    def handle(self) -> None:
        """Handle the command execution."""
        list_commands(self.app)
