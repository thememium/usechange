"""Global color constants for useChange CLI.

Usage:
    from usechange.cli.config.colors import COLOR

    console.print(f"[{COLOR.PRIMARY}]Hello[/]")
    console.print(f"[{COLOR.ERROR}]Failed[/]")
    console.print(f"[{COLOR.STYLE.HEADER}]Section[/]")
    print(f"{COLOR.ANSI.SECONDARY}styled text{COLOR.ANSI.RESET}")
"""

from __future__ import annotations

from typing import Final, final


@final
class COLOR:
    """Semantic color system for useChange CLI.

    All colors are defined as hex color codes compatible with Rich console.
    ANSI codes are available via COLOR.ANSI.* for non-Rich outputs.
    Style presets are available via COLOR.STYLE.* for common patterns.

    Examples:
        >>> console.print(f"[{COLOR.PRIMARY}]Hello World[/]")
        >>> console.print(f"[{COLOR.STYLE.HEADER}]Section[/]")
        >>> print(f"{COLOR.ANSI.SECONDARY}text{COLOR.ANSI.RESET}")
        >>> panel = Panel("Content", border_style=COLOR.SECONDARY)
    """

    # ==========================================================================
    # Hex Color Codes (for Rich console)
    # ==========================================================================

    # Brand colors
    PRIMARY: Final[str] = "#60D7FF"
    SECONDARY: Final[str] = "#5EFF87"
    ACCENT: Final[str] = "#F5FE53"

    # Functional colors
    SUCCESS: Final[str] = "#5EFF87"
    ERROR: Final[str] = "#FE686B"
    WARNING: Final[str] = "#F5FE53"
    INFO: Final[str] = "#60D7FF"

    # UI colors
    FOREGROUND: Final[str] = "#FFFFFF"
    FOREGROUND_MUTED: Final[str] = "#BBBBBB"
    BACKGROUND: Final[str] = "#000000"
    BORDER: Final[str] = "#60D7FF"
    BORDER_FOCUS: Final[str] = "#5EFF87"

    # Interactive elements
    COMMAND: Final[str] = "#60D7FF"
    OPTION: Final[str] = "#60D7FF"
    LINK: Final[str] = "#60D7FF"
    PROMPT: Final[str] = "#5EFF87"

    # Panel colors
    PANEL_PRIMARY: Final[str] = "#5EFF87"
    PANEL_SECONDARY: Final[str] = "#60D7FF"
    PANEL_ACCENT: Final[str] = "#F5FE53"

    # ==========================================================================
    # Nested: ANSI Escape Sequences (for non-Rich outputs like fzf)
    # ==========================================================================

    @final
    class ANSI:
        """ANSI escape sequences for terminal styling.

        Use these when you need to output styled text directly to the terminal
        without using Rich console (e.g., for fzf integration).

        Examples:
            >>> print(f"{COLOR.ANSI.SECONDARY}text{COLOR.ANSI.RESET}")
        """

        # Palette colors as ANSI
        PRIMARY: Final[str] = "\033[38;2;96;215;255m"
        SECONDARY: Final[str] = "\033[38;2;94;255;135m"
        ACCENT: Final[str] = "\033[38;2;216;176;0m"
        FOREGROUND: Final[str] = "\033[38;2;255;255;255m"
        FOREGROUND_MUTED: Final[str] = "\033[38;2;158;158;158m"

        # Standard ANSI colors
        RESET: Final[str] = "\033[0m"
        RED: Final[str] = "\033[31m"
        GREEN: Final[str] = "\033[32m"
        YELLOW: Final[str] = "\033[33m"
        BLUE: Final[str] = "\033[34m"


def bold(color: str) -> str:
    """Wrap color in bold tag for Rich.

    Usage:
        console.print(f"[{bold(COLOR.PRIMARY)}]Important![/]")
    """
    return f"bold {color}"


def style(text: str, color: str, *, bold: bool = False) -> str:
    """Apply color style to text for Rich console.

    Usage:
        console.print(style("Success!", COLOR.SUCCESS))
        console.print(style("Error", COLOR.ERROR, bold=True))
    """
    if bold:
        return f"[bold {color}]{text}[/bold {color}]"
    return f"[{color}]{text}[/{color}]"
