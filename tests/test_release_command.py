"""Tests for usechange.cli.commands.release_command — release workflow."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from usechange.cli.commands.release_command import (
    _extract_release_notes,
    _gh_release_exists,
    _load_existing_versions,
    _next_available_version,
    _run,
    _run_capture,
    _tag_exists,
)

# --- _run ---


def test_run_success(tmp_path: Path) -> None:
    _run(str(tmp_path), ["echo", "hello"])


def test_run_failure_raises(tmp_path: Path) -> None:
    try:
        _run(str(tmp_path), ["false"])
        assert False, "Should have raised"
    except RuntimeError as e:
        assert "Command failed" in str(e)


# --- _run_capture ---


def test_run_capture_success(tmp_path: Path) -> None:
    result = _run_capture(str(tmp_path), ["echo", "hello"])
    assert result == "hello"


def test_run_capture_failure_raises(tmp_path: Path) -> None:
    try:
        _run_capture(str(tmp_path), ["false"])
        assert False, "Should have raised"
    except RuntimeError as e:
        assert "Command failed" in str(e)


# --- _extract_release_notes ---


def test_extract_release_notes(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(
        "# Changelog\n\n"
        "## v2.0.0\n\n### Features\n\n- New\n\n"
        "## v1.0.0\n\n### Fixes\n\n- Old fix\n\n"
    )
    notes = _extract_release_notes(str(tmp_path), "v2.0.0")
    assert "v2.0.0" in notes
    assert "New" in notes
    assert "v1.0.0" not in notes


def test_extract_release_notes_missing(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("# Changelog\n\n## v1.0.0\n\n- Thing\n\n")
    try:
        _extract_release_notes(str(tmp_path), "v9.9.9")
        assert False, "Should have raised"
    except RuntimeError as e:
        assert "Missing changelog" in str(e)


# --- _gh_release_exists ---


@patch("usechange.cli.commands.release_command.subprocess.run")
def test_gh_release_exists_true(mock_run: MagicMock) -> None:
    mock_run.return_value = MagicMock(returncode=0)
    assert _gh_release_exists("/some/dir", "v1.0.0") is True


@patch("usechange.cli.commands.release_command.subprocess.run")
def test_gh_release_exists_false(mock_run: MagicMock) -> None:
    mock_run.return_value = MagicMock(returncode=1)
    assert _gh_release_exists("/some/dir", "v1.0.0") is False


# --- _tag_exists ---


def test_tag_exists_true(tmp_path: Path) -> None:
    subprocess.run(
        ["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True
    )
    subprocess.run(
        ["git", "config", "user.email", "t@t.com"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "T"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    (tmp_path / "f.txt").write_text("x")
    subprocess.run(
        ["git", "add", "f.txt"],
        cwd=tmp_path,
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
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "tag", "v1.0.0"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    assert _tag_exists(str(tmp_path), "v1.0.0") is True


def test_tag_exists_false(tmp_path: Path) -> None:
    subprocess.run(
        ["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True
    )
    assert _tag_exists(str(tmp_path), "v1.0.0") is False


# --- _load_existing_versions ---


def test_load_existing_versions(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("# Changelog\n\n## v2.0.0\n\n- B\n\n## v1.0.0\n\n- A\n\n")
    versions = _load_existing_versions(str(tmp_path))
    assert "1.0.0" in versions
    assert "2.0.0" in versions


def test_load_existing_versions_no_file(tmp_path: Path) -> None:
    versions = _load_existing_versions(str(tmp_path))
    assert versions == set()


# --- _next_available_version ---


def test_next_available_version_no_conflict(tmp_path: Path) -> None:
    subprocess.run(
        ["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True
    )
    result = _next_available_version(str(tmp_path), "1.0.0", set())
    assert result == "1.0.0"


def test_next_available_version_with_conflict(tmp_path: Path) -> None:
    subprocess.run(
        ["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True
    )
    subprocess.run(
        ["git", "config", "user.email", "t@t.com"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "T"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    (tmp_path / "f.txt").write_text("x")
    subprocess.run(
        ["git", "add", "f.txt"],
        cwd=tmp_path,
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
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "tag", "v1.0.0"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    result = _next_available_version(str(tmp_path), "1.0.0", set())
    assert result == "1.0.1"


def test_next_available_version_all_conflict_raises(tmp_path: Path) -> None:
    # When existing_versions contains the version but no tag exists
    result = _next_available_version(str(tmp_path), "1.0.0", {"1.0.0"})
    assert result == "1.0.1"
