from __future__ import annotations

import platform
from importlib.metadata import PackageNotFoundError, requires
from importlib.metadata import version as get_version

from rich.console import Console

from usechange.cli.config.colors import COLOR
from usechange.cli.core.base_command import BaseCommand

console = Console()


def _get_version() -> str:
    try:
        return get_version("usechange")
    except PackageNotFoundError:
        return "0.0.0"


def _get_dependencies() -> list[str]:
    """Get dependency names from package metadata."""
    try:
        reqs = requires("usechange")
        if not reqs:
            return []
        deps = []
        for req in reqs:
            # Parse package name from requirement string
            # Handles: "package>=1.0", "package[extra]>=1.0", etc.
            name = req.split("[")[0].split(">")[0].split("<")[0].split("=")[0].strip()
            if name and not req.startswith("("):
                deps.append(name)
        return deps
    except PackageNotFoundError:
        return []


class AboutCommand(BaseCommand):
    def signature(self) -> str:
        return "about"

    def description(self) -> str:
        return "Display detailed information about the application"

    def handle(self) -> None:
        version = _get_version()

        console.print()
        console.print(f"[bold {COLOR.PRIMARY}]Description[/bold {COLOR.PRIMARY}]")
        console.print(f"[{COLOR.PRIMARY}]─" * 78)
        console.print(
            "  An elegant CLI framework for Python with prefix matching, "
            "rich UI, and command scaffolding."
        )

        console.print()
        console.print(f"[bold {COLOR.PRIMARY}]Environment[/bold {COLOR.PRIMARY}]")
        console.print(f"[{COLOR.PRIMARY}]─" * 78)

        self._print_row("Application Name", "useChange")
        self._print_row("Application Version", version)
        self._print_row("Python Version", platform.python_version())
        self._print_row("Platform", f"[{COLOR.FOREGROUND_MUTED}]{platform.platform()}")

        console.print()
        console.print(f"[bold {COLOR.PRIMARY}]Entry Points[/bold {COLOR.PRIMARY}]")
        console.print(f"[{COLOR.PRIMARY}]─" * 78)

        self._print_row("usechange", "Primary command")
        self._print_row("change", "Alias")

        console.print()
        console.print(f"[bold {COLOR.PRIMARY}]Dependencies[/bold {COLOR.PRIMARY}]")
        console.print(f"[{COLOR.PRIMARY}]─" * 78)

        deps = _get_dependencies()
        if deps:
            for dep_name in deps:
                try:
                    installed_version = get_version(dep_name)
                    self._print_row(dep_name, installed_version)
                except Exception:
                    self._print_row(dep_name, "not installed")
        else:
            self._print_row("Dependencies", "unable to load")

        console.print()
        console.print(f"[bold {COLOR.PRIMARY}]Features[/bold {COLOR.PRIMARY}]")
        console.print(f"[{COLOR.PRIMARY}]─" * 78)

        self._print_row("Prefix Matching", f"[{COLOR.SECONDARY}]ENABLED")
        self._print_row("Rich UI", f"[{COLOR.SECONDARY}]ENABLED")
        self._print_row("Command Scaffolding", f"[{COLOR.SECONDARY}]ENABLED")
        self._print_row("Interactive Menus", f"[{COLOR.SECONDARY}]ENABLED")
        self._print_row("Fuzzy Finder", f"[{COLOR.SECONDARY}]ENABLED")
        console.print()

    def _print_row(self, label: str, value: str) -> None:
        visible_value = console.render_str(value).plain
        right_align_column = 76
        indent_width = 2
        padding_spaces = 2
        dots_length = (
            right_align_column
            - indent_width
            - len(label)
            - padding_spaces
            - len(visible_value)
        )
        dots = "." * max(dots_length, 1)
        console.print(
            f"  [{COLOR.FOREGROUND}]{label}[/{COLOR.FOREGROUND}] {dots} {value}"
        )
