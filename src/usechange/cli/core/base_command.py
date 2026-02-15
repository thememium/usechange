"""Base command class and custom help formatting for the CLI."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

import typer
from click import Argument, Option
from click.exceptions import Exit
from rich.console import Console
from typer.core import TyperCommand

from usechange.cli.config.colors import COLOR

if TYPE_CHECKING:
    from click.core import Context as ClickContext
    from click.formatting import HelpFormatter

console = Console()


class NestedCommandRegistry:
    """Registry for managing nested command groups and sub-apps.

    This registry maintains a mapping of group names to their Typer sub-apps,
    enabling commands with space-separated signatures like "usechange show" to be
    properly organized into command groups.
    """

    _instance: ClassVar[NestedCommandRegistry | None] = None
    _groups: dict[str, typer.Typer]
    _group_commands: dict[str, list[dict[str, Any]]]

    def __new__(cls) -> NestedCommandRegistry:
        """Ensure singleton pattern for the registry."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._groups = {}
            cls._instance._group_commands = {}
        return cls._instance

    def get_or_create_group(
        self, main_app: typer.Typer, group_name: str
    ) -> typer.Typer:
        """Get existing group or create a new sub-app for the group.

        Args:
            main_app: The main Typer application.
            group_name: The name of the command group (e.g., "change").

        Returns:
            The Typer sub-app for the group.
        """
        if group_name not in self._groups:
            # Create new sub-app for this group
            group_app = typer.Typer(
                help=f"Commands for {group_name}",
                invoke_without_command=True,
                no_args_is_help=False,
            )
            self._groups[group_name] = group_app
            self._group_commands[group_name] = []

            # Add the group app to main app
            main_app.add_typer(group_app, name=group_name)

            # Register the group callback to list subcommands
            self._register_group_callback(group_app, group_name)

        return self._groups[group_name]

    def _register_group_callback(self, group_app: typer.Typer, group_name: str) -> None:
        """Register a callback for the group that lists subcommands when no subcommand is given.

        Args:
            group_app: The Typer sub-app for the group.
            group_name: The name of the command group.
        """

        @group_app.callback()
        def group_callback(
            ctx: typer.Context,
            help_flag: bool = typer.Option(
                False, "--help", "-h", is_eager=True, help="Show help for this group"
            ),
        ) -> None:
            """Callback for the command group."""
            if help_flag:
                self._show_group_help(group_name)
                raise typer.Exit()

            if ctx.invoked_subcommand is None:
                self._show_group_commands(group_name)

    def _show_group_help(self, group_name: str) -> None:
        """Show help information for a command group.

        Args:
            group_name: The name of the command group.
        """
        console.print()
        console.print(f"[bold {COLOR.PRIMARY}]{group_name}[/bold {COLOR.PRIMARY}]")
        console.print(f"  Commands for managing {group_name}")
        console.print()
        self._show_group_commands(group_name)

    def _show_group_commands(self, group_name: str) -> None:
        """Display all commands in a group.

        Args:
            group_name: The name of the command group.
        """
        from usechange.cli.core.ui.list import list_group_commands

        group_app = self._groups.get(group_name)
        if group_app:
            list_group_commands(group_app, group_name)

    def register_command(
        self,
        group_name: str,
        command_name: str,
        description: str,
        callback: Any,
    ) -> None:
        """Register a command in the group's command list.

        Args:
            group_name: The name of the command group.
            command_name: The name of the command.
            description: The command description.
            callback: The command callback function.
        """
        if group_name not in self._group_commands:
            self._group_commands[group_name] = []

        self._group_commands[group_name].append(
            {
                "name": command_name,
                "description": description,
                "callback": callback,
            }
        )


class CustomHelpCommand(TyperCommand):
    """Custom help command with Rich-styled output."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the custom help command.

        Args:
            *args: Positional arguments passed to TyperCommand.
            **kwargs: Keyword arguments passed to TyperCommand.
        """
        context_settings = kwargs.get("context_settings") or {}
        context_settings["help_option_names"] = ["--help", "-h"]
        kwargs["context_settings"] = context_settings
        super().__init__(*args, **kwargs)

    def format_help(self, ctx: ClickContext, formatter: HelpFormatter) -> None:
        """Format help output with Rich styling.

        Args:
            ctx: The Click context.
            formatter: The help formatter.

        Raises:
            Exit: After displaying help.
        """
        arguments = [p for p in self.params if isinstance(p, Argument)]
        argument_names = [p.name for p in arguments if p.name]
        options = [
            p for p in self.params if isinstance(p, Option) and "--help" not in p.opts
        ]

        arg_usage = " ".join(rf"\[{name.upper()}]" for name in argument_names)
        usage = f"  [bold {COLOR.WARNING}]usechange {self.name}[/bold {COLOR.WARNING}] [bold {COLOR.PRIMARY}][OPTIONS]{f' {arg_usage}' if arg_usage else ''}[/bold {COLOR.PRIMARY}]"

        console.print()
        console.print(f"[bold {COLOR.SECONDARY}]Usage:[/bold {COLOR.SECONDARY}]")
        console.print(usage)
        console.print()

        option_flags = [", ".join(p.opts) for p in options]
        all_names = option_flags + argument_names
        longest_name_length = max(len(name) for name in all_names) if all_names else 0

        console.print(f"[bold {COLOR.SECONDARY}]Options:")

        help_flags = "--help, -h"
        help_padding = " " * (longest_name_length - len(help_flags) + 12)
        console.print(
            f"  [{COLOR.OPTION}]{help_flags}[/{COLOR.OPTION}]{help_padding}Show this message and exit."
        )

        for param in options:
            flags = ", ".join(param.opts)
            description = getattr(param, "help", "") or ""
            padding = " " * (longest_name_length - len(flags) + 12)
            console.print(
                f"  [{COLOR.OPTION}]{flags}[/{COLOR.OPTION}]{padding}{description}"
            )

        console.print()

        if arguments:
            console.print(f"[bold {COLOR.SECONDARY}]Arguments:")

            for param in arguments:
                name = param.name or "arg"
                description = getattr(param, "help", "") or ""
                padding = " " * (longest_name_length - len(name) + 12)
                console.print(
                    f"  [{COLOR.OPTION}]{name}[/{COLOR.OPTION}]{padding}{description}"
                )

            console.print()

        raise Exit()


class BaseCommand(ABC):
    """Abstract base class for CLI commands.

    All commands must inherit from this class and implement the
    handle(), signature(), and description() methods.
    """

    def __init__(self, app: typer.Typer) -> None:
        """Initialize the command and register it with the app.

        Args:
            app: The Typer application instance.
        """
        self.app = app
        self.register()

    @abstractmethod
    def handle(self, *args: Any, **kwargs: Any) -> None:
        """Execute the command.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        pass

    @abstractmethod
    def signature(self) -> str:
        """Return the command signature.

        Returns:
            The command signature (e.g., "make:command").
        """
        pass

    @abstractmethod
    def description(self) -> str:
        """Return the command description.

        Returns:
            A short description of what the command does.
        """
        pass

    def visible(self) -> bool:
        return True

    def register(self) -> None:
        if not self.visible():
            return

        signature = self.signature()
        signature_parts = signature.split()

        # Check if this is a space-separated nested command signature (e.g., "usechange show")
        # vs a command with argument placeholders (e.g., "test-cmd <name>")
        # Only 2-part signatures where the second part is a valid subcommand
        # name are treated as nested commands
        # Colon-separated signatures (e.g., "config:set") are registered as single
        # commands and grouped into sections by the list display logic
        if len(signature_parts) == 2 and self._is_valid_subcommand_name(
            signature_parts[1]
        ):
            # Space-separated nested command (e.g., "usechange show", "change list")
            group_name = signature_parts[0]
            command_name = signature_parts[1]

            registry = NestedCommandRegistry()
            group_app = registry.get_or_create_group(self.app, group_name)

            cmd_decorator = group_app.command(
                name=command_name,
                help=self.description(),
                cls=CustomHelpCommand,
            )
            cmd_decorator(self.handle)
        else:
            # Single-level command (e.g., "help", "init", "config:set", "make:command")
            name = signature_parts[0]
            cmd_decorator = self.app.command(
                name=name,
                help=self.description(),
                cls=CustomHelpCommand,
            )
            cmd_decorator(self.handle)

    def _is_valid_subcommand_name(self, name: str) -> bool:
        """Check if a string is a valid subcommand name (not an argument placeholder).

        Valid subcommand names:
        - Are simple identifiers (letters, numbers, hyphens, underscores)
        - Do NOT contain argument markers like < > [ ] --

        Args:
            name: The string to check.

        Returns:
            True if the string is a valid subcommand name.
        """
        # Argument placeholders contain these characters
        argument_markers = {"<", ">", "[", "]", "--"}

        for marker in argument_markers:
            if marker in name:
                return False

        # Valid subcommand names are simple identifiers
        return name.replace("-", "").replace("_", "").isalnum()
