"""Command listing utilities for useChange CLI."""

from __future__ import annotations

from typing import TYPE_CHECKING

import click
import typer
from rich.console import Console

from usechange.cli.config.colors import COLOR
from usechange.cli.core.ui.title import print_title

if TYPE_CHECKING:
    pass

console = Console()

SPACER_LENGTH = 18

def list_commands(app: typer.Typer, prefix_filter: str | None = None) -> None:
    """List all available commands with optional filtering.

    Displays commands in a formatted list with sections for grouped commands
    (those with colons in their names).

    Args:
        app: The Typer application instance.
        prefix_filter: Optional prefix to filter commands by name.
    """
    print_title()

    click_group = typer.main.get_command(app)

    all_command_names = [cmd.name for cmd in app.registered_commands if cmd.name]
    longest_name_length = (
        max(len(name) for name in all_command_names) if all_command_names else 0
    )

    console.print(f"[bold {COLOR.SECONDARY}]Usage:[/bold {COLOR.SECONDARY}]")
    console.print(f"  [{COLOR.PRIMARY}]usechange [OPTIONS] [ARGUMENTS]")
    console.print()

    console.print(f"[bold {COLOR.SECONDARY}]Options:")

    help_flags = "--help, -h"
    help_padding = " " * (longest_name_length - len(help_flags) + SPACER_LENGTH)
    console.print(
        f"  [{COLOR.OPTION}]{help_flags}[/{COLOR.OPTION}]{help_padding}Show this message and exit."
    )

    if click_group.params:
        for param in click_group.params:
            flags = ", ".join(param.opts)
            if "--help" in flags:
                continue
            description = getattr(param, "help", "") or ""
            padding = " " * (longest_name_length - len(flags) + SPACER_LENGTH)
            console.print(
                f"  [{COLOR.OPTION}]{flags}[/{COLOR.OPTION}]{padding}{description}"
            )
    console.print()

    commands: list[dict[str, str]] = []
    for command in app.registered_commands:
        callback = command.callback
        name = command.name or (
            getattr(callback, "__name__", "unknown") if callback else "unknown"
        )
        help_text = command.help or ""
        commands.append({"name": name, "help": help_text})

    commands.sort(key=lambda x: x["name"])

    if prefix_filter:
        filtered = [c for c in commands if c["name"].startswith(prefix_filter)]
        if not filtered:
            console.print(f"  [dim]No commands found for '{prefix_filter}'[/dim]")
            console.print()
            return
        commands = filtered

    if not prefix_filter:
        console.print(f"[bold {COLOR.SECONDARY}]Available commands:")

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

    all_names = all_command_names + list(groups.keys())
    if all_names:
        longest_name_length = max(len(name) for name in all_names)

    def print_command(cmd: dict[str, str]) -> None:
        """Print a single command with proper formatting."""
        padding = " " * (longest_name_length - len(cmd["name"]) + SPACER_LENGTH)
        console.print(
            f"  [{COLOR.COMMAND}]{cmd['name']}[/{COLOR.COMMAND}]{padding}{cmd['help']}"
        )

    for group_name, group_help in groups.items():
        top_level.append({"name": group_name, "help": group_help})

    top_level.sort(key=lambda x: x["name"])

    if top_level:
        for cmd in top_level:
            print_command(cmd)
        console.print()

    sections: dict[str, list[dict[str, str]]] = {}
    for cmd in with_colon:
        section_prefix = cmd["name"].split(":")[0]
        if section_prefix not in sections:
            sections[section_prefix] = []
        sections[section_prefix].append(cmd)

    for section_prefix, section_cmds in sections.items():
        console.print(f"[bold {COLOR.SECONDARY}]{section_prefix}:")
        for cmd in section_cmds:
            print_command(cmd)
        console.print()


def list_group_commands(group_app: typer.Typer, group_name: str) -> None:
    """List all commands within a specific command group.

    Displays commands in a formatted list for a nested command group,
    similar to how list_commands works for the main app.

    Args:
        group_app: The Typer sub-app for the command group.
        group_name: The name of the command group.
    """
    all_command_names = [cmd.name for cmd in group_app.registered_commands if cmd.name]
    longest_name_length = (
        max(len(name) for name in all_command_names) if all_command_names else 0
    )

    console.print(f"[bold {COLOR.SECONDARY}]Usage:[/bold {COLOR.SECONDARY}]")
    console.print(f"  [{COLOR.PRIMARY}]usechange {group_name} [COMMAND] [OPTIONS][/]")
    console.print()

    console.print(f"[bold {COLOR.SECONDARY}]Options:")
    help_flags = "--help, -h"
    help_padding = " " * (longest_name_length - len(help_flags) + SPACER_LENGTH)
    console.print(
        f"  [{COLOR.OPTION}]{help_flags}[/{COLOR.OPTION}]{help_padding}Show this message and exit."
    )
    console.print()

    commands: list[dict[str, str]] = []
    for command in group_app.registered_commands:
        callback = command.callback
        name = command.name or (
            getattr(callback, "__name__", "unknown") if callback else "unknown"
        )
        help_text = command.help or ""
        commands.append({"name": name, "help": help_text})

    commands.sort(key=lambda x: x["name"])

    console.print(f"[bold {COLOR.SECONDARY}]Available commands:")

    for cmd in commands:
        padding = " " * (longest_name_length - len(cmd["name"]) + SPACER_LENGTH)
        console.print(
            f"  [{COLOR.COMMAND}]{cmd['name']}[/{COLOR.COMMAND}]{padding}{cmd['help']}"
        )

    console.print()
