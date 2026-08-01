"""Tests for usechange.cli.commands — print_error."""

from __future__ import annotations

from usechange.cli.commands import print_error


def test_print_error_runs_without_crash() -> None:
    # Just verify it doesn't raise — it prints to console
    print_error("test error message")
