"""Fzf command for interactive command finder."""

from __future__ import annotations

import inspect
import os
import subprocess
import sys
from typing import TYPE_CHECKING, Any

import click
import typer
from rich.console import Console
from rich.prompt import Confirm, IntPrompt

from usechange.cli.config.colors import COLOR
from usechange.cli.core.base_command import BaseCommand
from usechange.cli.core.error.handler import ErrorHandler
from usechange.cli.core.exceptions import UsechangeError
from usechange.cli.utils.interactive.terminal_menu import terminal_menu

if TYPE_CHECKING:
    from click.core import Command as ClickCommand

console = Console()


class FzfCommand(BaseCommand):
    """Interactive command finder using fzf."""

    def signature(self) -> str:
        """Return the command signature."""
        return "fzf"

    def description(self) -> str:
        """Return the command description."""
        return "Interactive command finder using fzf"

    def _get_required_arguments(
        self, command: ClickCommand
    ) -> list[tuple[str, str, type]]:
        """Get required arguments for a command.

        Args:
            command: The Click command to inspect.

        Returns:
            List of tuples containing (name, help_text, type).
        """
        callback = command.callback
        if not callback:
            return []

        required: list[tuple[str, str, type]] = []
        sig = inspect.signature(callback)
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            is_required = False

            if param.default is inspect.Parameter.empty:
                is_required = True
            elif hasattr(param.default, "default") and param.default.default is ...:
                is_required = True

            if is_required:
                help_text = ""
                try:
                    help_text = getattr(param.default, "help", "") or ""
                except AttributeError:
                    pass

                param_type: type = param.annotation
                if param_type is inspect.Parameter.empty:
                    param_type = str

                required.append((param_name, help_text, param_type))

        return required

    def _get_optional_options(
        self, command: ClickCommand
    ) -> list[tuple[str, str, str, type]]:
        """Get optional options for a command.

        Args:
            command: The Click command to inspect.

        Returns:
            List of tuples containing (name, option_names, help_text, type).
        """
        callback = command.callback
        if not callback:
            return []

        options: list[tuple[str, str, str, type]] = []
        sig = inspect.signature(callback)
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            is_option = False
            default_value = param.default

            if default_value is inspect.Parameter.empty:
                continue

            if hasattr(default_value, "default"):
                if default_value.default is not ...:
                    is_option = True
            else:
                is_option = True

            if is_option:
                option_names = ""
                try:
                    param_decls = getattr(default_value, "param_decls", [])
                    if param_decls:
                        option_names = ", ".join(param_decls)
                    else:
                        option_names = f"--{param_name.replace('_', '-')}"
                except AttributeError:
                    option_names = f"--{param_name.replace('_', '-')}"

                if "--help" in option_names:
                    continue

                help_text = ""
                try:
                    help_text = getattr(default_value, "help", "") or ""
                except AttributeError:
                    pass

                param_type: type = param.annotation
                if param_type is inspect.Parameter.empty:
                    param_type = str

                options.append((param_name, option_names, help_text, param_type))

        return options

    def _run_fzf_menu(
        self,
        options: list[str],
        prompt: str = "useChange » ",
    ) -> str | None:
        """Run fzf with given options and return selection.

        Args:
            options: List of formatted option strings to display.
            prompt: The prompt to show in fzf.

        Returns:
            The selected string or None if cancelled.
        """
        input_data = "\n".join(options)

        fzf_args = [
            "fzf",
            "--ansi",
            f"--prompt={prompt}",
            f"--color=prompt:{COLOR.SECONDARY}",
            "--layout=reverse",
            "--height=~40%",
            "--border",
            f"--color=border:{COLOR.PRIMARY}",
            "--bind=ctrl-d:half-page-down",
            "--bind=ctrl-u:half-page-up",
        ]

        try:
            result = subprocess.run(
                fzf_args,
                input=input_data,
                capture_output=True,
                text=True,
            )

            if result.returncode == 130 or not result.stdout.strip():
                return None

            if result.returncode != 0:
                ErrorHandler.display_error(
                    f"fzf error: {result.stderr}",
                    suggestion="Check fzf installation and try again",
                )
                raise typer.Exit(code=1)

            return result.stdout.strip()

        except FileNotFoundError:
            raise UsechangeError(
                "fzf is not installed",
                suggestion="Install fzf: https://github.com/junegunn/fzf#installation",
            )

    def _get_group_subcommands(self, group_name: str) -> list[dict[str, Any]]:
        """Get subcommands for a command group.

        Args:
            group_name: The name of the command group.

        Returns:
            List of subcommand dictionaries with name, help, and command.
        """
        from usechange.cli.core.base_command import NestedCommandRegistry

        registry = NestedCommandRegistry()
        group_app = registry._groups.get(group_name)

        if not group_app:
            return []

        subcommands: list[dict[str, Any]] = []
        for command in group_app.registered_commands:
            name = command.name or "unknown"
            help_text = command.help or ""
            subcommands.append({"name": name, "help": help_text, "command": command})

        return subcommands

    def handle(
        self,
        extra_args: list[str] = typer.Argument(
            None, help="Additional arguments to pass to the selected command"
        ),
    ) -> None:
        """Handle the fzf command execution.

        Args:
            extra_args: Additional arguments to pass to the selected command.
        """
        app = self.app
        commands: list[dict[str, Any]] = []

        for command in app.registered_commands:
            name = command.name or "unknown"
            help_text = command.help or ""
            commands.append({"name": name, "help": help_text, "command": command})

        if not commands:
            ErrorHandler.display_error("No commands available")
            raise typer.Exit(code=1)

        # Detect command groups (nested commands like "schema", "change", etc.)
        click_group = typer.main.get_command(app)
        groups: dict[str, str] = {}
        if isinstance(click_group, click.Group):
            for cmd_name, cmd_obj in click_group.commands.items():
                if isinstance(cmd_obj, click.Group):
                    groups[cmd_name] = (
                        getattr(cmd_obj, "help", f"Commands for {cmd_name}")
                        or f"Commands for {cmd_name}"
                    )

        top_level = [
            c for c in commands if ":" not in c["name"] and c["name"] not in groups
        ]
        with_colon = [c for c in commands if ":" in c["name"]]

        top_level.sort(key=lambda x: x["name"])

        sections: dict[str, list[dict[str, Any]]] = {}
        for cmd in with_colon:
            section_prefix = cmd["name"].split(":")[0]
            if section_prefix not in sections:
                sections[section_prefix] = []
            sections[section_prefix].append(cmd)

        for section_cmds in sections.values():
            section_cmds.sort(key=lambda x: x["name"])
        sorted_sections = sorted(sections.items(), key=lambda x: x[0])

        # Add groups to top_level for selection
        for group_name, group_help in groups.items():
            top_level.append({"name": group_name, "help": group_help, "is_group": True})

        ordered_commands = top_level + [
            cmd for _, section_cmds in sorted_sections for cmd in section_cmds
        ]
        max_name_len = max(len(cmd["name"]) for cmd in ordered_commands)

        options: list[str] = []
        for cmd in ordered_commands:
            padding = " " * (max_name_len - len(cmd["name"]) + 4)
            line = f"{COLOR.ANSI.PRIMARY}{cmd['name']}{COLOR.ANSI.RESET}{padding}{COLOR.ANSI.FOREGROUND_MUTED}{cmd['help']}{COLOR.ANSI.RESET}"
            options.append(line)

        # First fzf menu - select command or group
        selection = self._run_fzf_menu(options, prompt="useChange » ")

        if selection is None:
            ErrorHandler.display_warning("No command selected")
            return

        cmd_name = selection.split()[0] if selection else None

        if not cmd_name:
            ErrorHandler.display_error("Could not parse command")
            raise typer.Exit(code=1)

        selected_cmd = next(
            (c for c in ordered_commands if c["name"] == cmd_name), None
        )

        # Check if a group was selected
        if selected_cmd and selected_cmd.get("is_group"):
            # Show nested fzf for subcommands
            subcommands = self._get_group_subcommands(cmd_name)

            if not subcommands:
                ErrorHandler.display_error(f"No subcommands found for '{cmd_name}'")
                raise typer.Exit(code=1)

            subcommands.sort(key=lambda x: x["name"])
            max_sub_name_len = max(len(cmd["name"]) for cmd in subcommands)

            sub_options: list[str] = []
            for cmd in subcommands:
                padding = " " * (max_sub_name_len - len(cmd["name"]) + 4)
                line = f"{COLOR.ANSI.PRIMARY}{cmd['name']}{COLOR.ANSI.RESET}{padding}{COLOR.ANSI.FOREGROUND_MUTED}{cmd['help']}{COLOR.ANSI.RESET}"
                sub_options.append(line)

            sub_selection = self._run_fzf_menu(
                sub_options, prompt=f"usechange {cmd_name} » "
            )

            if sub_selection is None:
                ErrorHandler.display_warning("No subcommand selected")
                return

            sub_name = sub_selection.split()[0] if sub_selection else None

            if not sub_name:
                ErrorHandler.display_error("Could not parse subcommand")
                raise typer.Exit(code=1)

            selected_sub = next((c for c in subcommands if c["name"] == sub_name), None)

            # Update cmd_name to full path (e.g., "schema list")
            cmd_name = f"{cmd_name} {sub_name}"
            selected_cmd = selected_sub

        extra = " ".join(extra_args) if extra_args else ""

        required_args = (
            self._get_required_arguments(selected_cmd["command"])
            if selected_cmd
            else []
        )
        if required_args:
            help_result = subprocess.run(
                f"usechange {cmd_name} --help",
                shell=True,
                capture_output=True,
                text=True,
                env={**os.environ, "FORCE_COLOR": "1", "CLICOLOR_FORCE": "1"},
            )
            sys.stdout.write(help_result.stdout)

            console.rule(
                title=f"[bold {COLOR.PRIMARY}]── Enter required arguments for '{cmd_name}':[/bold {COLOR.PRIMARY}]",
                align="left",
                style=COLOR.PRIMARY,
            )
            console.print()

            arg_values: list[str] = []
            for arg_name, arg_help, arg_type in required_args:
                value: str | None = None

                if arg_type is bool:
                    enabled = Confirm.ask(
                        f"[bold {COLOR.SECONDARY}]Enable '{arg_name}'?[/bold {COLOR.SECONDARY}]"
                        + (f" ({arg_help})" if arg_help else ""),
                        default=True,
                    )
                    value = "true" if enabled else "false"
                    if enabled:
                        console.print(
                            f"[[bold {COLOR.SECONDARY}]✓[/bold {COLOR.SECONDARY}]] {arg_name} enabled"
                        )
                    else:
                        console.print(
                            f"[[bold {COLOR.ERROR}]✗[/bold {COLOR.ERROR}]] {arg_name} disabled"
                        )
                    console.print()
                elif arg_type is int:
                    int_value = IntPrompt.ask(
                        f"[bold {COLOR.SECONDARY}]Enter value for '{arg_name}'[/bold {COLOR.SECONDARY}]"
                        + (f" ({arg_help})" if arg_help else "")
                    )
                    value = str(int_value)
                else:
                    value = ""
                    while not value:
                        prompt_text = f"Enter value for '{arg_name}'"
                        if arg_help:
                            prompt_text += f" ({arg_help})"
                        prompt_text += ":"
                        console.print(f"[bold {COLOR.SECONDARY}]{prompt_text}")
                        console.print(f"[bold {COLOR.SECONDARY}]└─> ", end="")

                        try:
                            user_input = input()
                            value = user_input.strip()
                        except EOFError:
                            value = ""
                        except KeyboardInterrupt:
                            ErrorHandler.display_warning("Cancelled by user")
                            raise typer.Exit(code=0)

                        if not value:
                            console.print(
                                f"[{COLOR.ERROR}]Value is required. Please enter a value.[/{COLOR.ERROR}]"
                            )

                    if " " in value:
                        value = f'"{value}"'
                    arg_values.append(value)

            if arg_values:
                extra = " ".join(arg_values)

        optional_options = (
            self._get_optional_options(selected_cmd["command"]) if selected_cmd else []
        )
        if optional_options:
            console.print()
            console.print(
                f"[bold {COLOR.SECONDARY}]Select optional flags (space to select, enter to confirm):[/bold {COLOR.SECONDARY}]"
            )
            menu_options: list[str] = []
            for param_name, option_names, help_text, opt_type in optional_options:
                type_name = (
                    opt_type.__name__
                    if hasattr(opt_type, "__name__")
                    else str(opt_type)
                )
                display = option_names
                if type_name != "str":
                    display += f" [{type_name}]"
                if help_text:
                    display += f" - {help_text}"
                menu_options.append(display)

            selected_options = terminal_menu(
                menu_options,
                multi_select=True,
            )

            if not selected_options:
                ErrorHandler.display_warning("No optional flags selected")
            else:
                for opt in selected_options:
                    console.print(
                        f"  [[bold {COLOR.PRIMARY}]*[/bold {COLOR.PRIMARY}]] {opt}"
                    )
                console.print()

                option_values: list[str] = []
                for selected_option in selected_options:
                    idx = menu_options.index(selected_option)
                    (
                        param_name,
                        option_names,
                        help_text,
                        opt_type,
                    ) = optional_options[idx]
                    first_flag = option_names.split(",")[0].strip()

                    opt_value: str | None = None
                    if opt_type is bool:
                        enabled = Confirm.ask(
                            f"[bold {COLOR.SECONDARY}]Enable {first_flag}?"
                            + (f" ({help_text})" if help_text else ""),
                            default=True,
                        )
                        if enabled:
                            option_values.append(first_flag)
                            console.print(
                                f"[[bold {COLOR.SECONDARY}]✓[/bold {COLOR.SECONDARY}]] {first_flag} enabled"
                            )
                        else:
                            console.print(
                                f"[[bold {COLOR.ERROR}]✗[/bold {COLOR.ERROR}]] {first_flag} disabled"
                            )
                        console.print()
                    elif opt_type is int:
                        int_value = IntPrompt.ask(
                            f"[bold {COLOR.SECONDARY}]Value for {first_flag}"
                            + (f" ({help_text})" if help_text else "")
                        )
                        option_values.append(f"{first_flag} {int_value}")
                    else:
                        opt_value = ""
                        while not opt_value:
                            prompt_text = (
                                f"[bold {COLOR.SECONDARY}]Value for {first_flag}"
                            )
                            if help_text:
                                prompt_text += f" ({help_text})"
                            prompt_text += ":"
                            console.print(prompt_text)
                            console.print(f"[bold {COLOR.SECONDARY}]└─> ", end="")
                            try:
                                opt_value = input().strip()
                            except KeyboardInterrupt:
                                ErrorHandler.display_warning("Cancelled by user")
                                raise typer.Exit(code=0)
                            if not opt_value:
                                console.print(
                                    f"[{COLOR.ERROR}]Value is required. Please enter a value or press Ctrl+C to cancel.[/{COLOR.ERROR}]"
                                )
                        if " " in opt_value:
                            opt_value = f'"{opt_value}"'
                        option_values.append(f"{first_flag} {opt_value}")
                if option_values:
                    extra = (
                        f"{extra} {' '.join(option_values)}"
                        if extra
                        else " ".join(option_values)
                    )

        full_cmd = f"usechange {cmd_name}{' ' + extra if extra else ''}"

        console.print()
        console.rule(
            f"[bold {COLOR.PRIMARY}]── Running Command:",
            align="left",
            style=COLOR.PRIMARY,
        )
        console.print()
        console.print(f"[bold {COLOR.WARNING}]{full_cmd}")
        console.print()

        subprocess.run(full_cmd, shell=True)

        try:
            pass
        except KeyboardInterrupt:
            ErrorHandler.display_warning("Cancelled by user")
            raise typer.Exit(code=0)
