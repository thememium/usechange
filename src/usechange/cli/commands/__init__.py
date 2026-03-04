from __future__ import annotations

from usecli import COLOR, console


def print_error(message: str) -> None:
    error_prefix = f"[bold black on {COLOR.ERROR}] ERROR [/bold black on {COLOR.ERROR}]"
    error_msg = f"[bold {COLOR.ERROR}]{message}[/bold {COLOR.ERROR}]"
    console.print()
    console.print(f"{error_prefix} {error_msg}")
    console.print()
