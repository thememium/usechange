"""Title display utilities for useChange CLI."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, metadata

from rich.console import Console

from usechange.cli.config.colors import COLOR

console = Console()


def get_project_name() -> str:
    """Get the project name from package metadata.

    Returns:
        The project name from package metadata, or "usechange" if not found.
    """
    try:
        meta = metadata("usechange")
        name = meta["Name"] if "Name" in meta else "usechange"
        return name.replace("change", "Change")
    except PackageNotFoundError:
        return "usechange"


def print_title(title: str | None = None) -> None:
    """Print an ASCII art title, otherwise plain text.

    Args:
        title: Optional custom title text. If not provided, uses ASCII art.
    """
    try:
        title_text = """
                           ▄▄█▀▀▀▄█ ▀██                                       
 ▄▄▄ ▄▄▄   ▄▄▄▄    ▄▄▄▄  ▄█▀     ▀   ██ ▄▄    ▄▄▄▄   ▄▄ ▄▄▄     ▄▄▄ ▄   ▄▄▄▄  
  ██  ██  ██▄ ▀  ▄█▄▄▄██ ██          ██▀ ██  ▀▀ ▄██   ██  ██   ██ ██  ▄█▄▄▄██ 
  ██  ██  ▄ ▀█▄▄ ██      ▀█▄      ▄  ██  ██  ▄█▀ ██   ██  ██    █▀▀   ██      
  ▀█▄▄▀█▄ █▀▄▄█▀  ▀█▄▄▄▀  ▀▀█▄▄▄▄▀  ▄██▄ ██▄ ▀█▄▄▀█▀ ▄██▄ ██▄  ▀████▄  ▀█▄▄▄▀ 
                                                             ▄█▄▄▄▄▀         
 █████▓▓▓▓▓▒▒▒▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▒▒▒▒▒▓▓▓▓▓█████
        """

        console.print(f"[{COLOR.PRIMARY}]{title_text}")
    except (ImportError, ModuleNotFoundError):
        console.print(f"[bold {COLOR.SECONDARY}]{title}[/bold {COLOR.SECONDARY}]\n")
