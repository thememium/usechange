"""Tests for ReleaseCommand metadata and version logic."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import typer

from usechange.cli.commands.release_command import (
    ReleaseCommand,
    _next_available_version,
)

app = typer.Typer()


def _init_repo(path: Path) -> None:
    subprocess.run(
        ["git", "init"], cwd=path, check=True, capture_output=True, text=True
    )
    subprocess.run(
        ["git", "config", "user.email", "t@t.com"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "T"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
    (path / "f.txt").write_text("x")
    subprocess.run(
        ["git", "add", "f.txt"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=T",
            "-c",
            "user.email=t@t.com",
            "commit",
            "-m",
            "init",
            "-m",
            "body",
        ],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )


# --- ReleaseCommand metadata ---


def test_release_command_signature() -> None:
    cmd = ReleaseCommand(app)
    assert cmd.signature() == "release"


def test_release_command_description() -> None:
    cmd = ReleaseCommand(app)
    assert "release" in cmd.description().lower()


@patch("usechange.cli.commands.release_command.Confirm.ask", return_value=False)
def test_handle_cancelled(mock_confirm) -> None:
    cmd = ReleaseCommand(app)
    cmd.handle(directory=None, yes=False, no_date=False, no_emojis=False)
    mock_confirm.assert_called_once()


@patch("usechange.cli.commands.release_command.Confirm.ask", return_value=True)
def test_handle_no_head(mock_confirm, tmp_path: Path) -> None:
    cmd = ReleaseCommand(app)
    cmd.handle(directory=str(tmp_path), yes=True, no_date=False, no_emojis=False)


# --- _next_available_version ---


def test_next_available_version_with_tag_conflict(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    subprocess.run(
        ["git", "tag", "v1.0.0"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    result = _next_available_version(str(tmp_path), "1.0.0", set())
    assert result == "1.0.1"


def test_next_available_version_in_existing_set(tmp_path: Path) -> None:
    result = _next_available_version(str(tmp_path), "1.0.0", {"1.0.0"})
    assert result == "1.0.1"


def test_next_available_version_multiple_conflicts(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    subprocess.run(
        ["git", "tag", "v1.0.0"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "tag", "v1.0.1"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    result = _next_available_version(str(tmp_path), "1.0.0", set())
    assert result == "1.0.2"
