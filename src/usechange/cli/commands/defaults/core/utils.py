"""Shared utilities for useChange commands."""

from __future__ import annotations

import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console

if TYPE_CHECKING:
    pass

console = Console()


def is_interactive() -> bool:
    """Check if the current terminal is interactive.

    Returns:
        True if stdin is a tty, False otherwise.
    """
    return sys.stdin.isatty()
