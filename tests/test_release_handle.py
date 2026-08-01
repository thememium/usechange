"""Tests for ReleaseCommand.handle — full workflow with mocked externals."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import typer

from usechange.cli.commands.release_command import ReleaseCommand

app = typer.Typer()


@patch("usechange.cli.commands.release_command._run")
@patch("usechange.cli.commands.release_command._run_capture", return_value="abc123")
@patch(
    "usechange.cli.commands.release_command._extract_release_notes",
    return_value="## v1.1.0\n\n- New\n\n",
)
@patch("usechange.cli.commands.release_command._gh_release_exists", return_value=False)
@patch(
    "usechange.cli.commands.release_command._load_existing_versions", return_value=set()
)
@patch(
    "usechange.cli.commands.release_command._next_available_version",
    return_value="1.1.0",
)
@patch("usechange.changelog.cli.default.run_changelog")
@patch("usechange.changelog.git.has_head", return_value=True)
@patch("usechange.cli.commands.release_command.Confirm.ask", return_value=True)
def test_handle_full_release_flow(
    mock_confirm,
    mock_has_head,
    mock_run_changelog,
    mock_next_version,
    mock_load_versions,
    mock_gh_exists,
    mock_extract_notes,
    mock_run_capture,
    mock_run,
    tmp_path: Path,
) -> None:
    from usechange.changelog.cli.default import ChangelogResult

    mock_run_changelog.return_value = ChangelogResult(
        message="Generated",
        content="# Changelog\n\n## v1.1.0\n\n- New\n\n",
        output_path="CHANGELOG.md",
        new_version="1.1.0",
        wrote_file=True,
        resolved_dir=str(tmp_path),
    )

    cmd = ReleaseCommand(app)
    cmd.handle(directory=str(tmp_path), yes=False, no_date=False, no_emojis=False)

    mock_confirm.assert_called_once()
    mock_has_head.assert_called_once()
    mock_run_changelog.assert_called_once()
    # _run should be called for uv and git commands
    assert mock_run.call_count >= 6


@patch("usechange.cli.commands.release_command._run")
@patch("usechange.cli.commands.release_command._run_capture", return_value="abc123")
@patch(
    "usechange.cli.commands.release_command._extract_release_notes",
    return_value="## v1.1.0\n\n- New\n\n",
)
@patch("usechange.cli.commands.release_command._gh_release_exists", return_value=True)
@patch(
    "usechange.cli.commands.release_command._load_existing_versions", return_value=set()
)
@patch(
    "usechange.cli.commands.release_command._next_available_version",
    return_value="1.1.0",
)
@patch("usechange.changelog.cli.default.run_changelog")
@patch("usechange.changelog.git.has_head", return_value=True)
@patch("usechange.cli.commands.release_command.Confirm.ask", return_value=True)
def test_handle_release_with_existing_gh_release(
    mock_confirm,
    mock_has_head,
    mock_run_changelog,
    mock_next_version,
    mock_load_versions,
    mock_gh_exists,
    mock_extract_notes,
    mock_run_capture,
    mock_run,
    tmp_path: Path,
) -> None:
    from usechange.changelog.cli.default import ChangelogResult

    mock_run_changelog.return_value = ChangelogResult(
        message="Generated",
        content="# Changelog\n\n## v1.1.0\n\n- New\n\n",
        output_path="CHANGELOG.md",
        new_version="1.1.0",
        wrote_file=True,
        resolved_dir=str(tmp_path),
    )

    cmd = ReleaseCommand(app)
    cmd.handle(directory=str(tmp_path), yes=False, no_date=False, no_emojis=False)

    # Should call gh release edit instead of create
    gh_calls = [c for c in mock_run.call_args_list if "gh" in str(c)]
    assert len(gh_calls) >= 1
    assert "edit" in str(gh_calls[0])


@patch("usechange.cli.commands.release_command._run")
@patch("usechange.cli.commands.release_command._run_capture", return_value="abc123")
@patch(
    "usechange.cli.commands.release_command._extract_release_notes",
    return_value="## v1.1.0\n\n- New\n\n",
)
@patch("usechange.cli.commands.release_command._gh_release_exists", return_value=False)
@patch(
    "usechange.cli.commands.release_command._load_existing_versions", return_value=set()
)
@patch(
    "usechange.cli.commands.release_command._next_available_version",
    return_value="1.1.1",
)
@patch("usechange.changelog.cli.default.run_changelog")
@patch("usechange.changelog.git.has_head", return_value=True)
@patch("usechange.cli.commands.release_command.Confirm.ask", return_value=True)
def test_handle_release_version_conflict(
    mock_confirm,
    mock_has_head,
    mock_run_changelog,
    mock_next_version,
    mock_load_versions,
    mock_gh_exists,
    mock_extract_notes,
    mock_run_capture,
    mock_run,
    tmp_path: Path,
) -> None:
    from usechange.changelog.cli.default import ChangelogResult

    mock_run_changelog.return_value = ChangelogResult(
        message="Generated",
        content="# Changelog\n\n## v1.1.0\n\n- New\n\n",
        output_path="CHANGELOG.md",
        new_version="1.1.0",
        wrote_file=True,
        resolved_dir=str(tmp_path),
    )

    cmd = ReleaseCommand(app)
    cmd.handle(directory=str(tmp_path), yes=False, no_date=False, no_emojis=False)

    # run_changelog should be called twice (once for initial, once for bumped version)
    assert mock_run_changelog.call_count == 2


@patch("usechange.changelog.git.has_head", return_value=True)
@patch("usechange.changelog.cli.default.run_changelog")
@patch("usechange.cli.commands.release_command.Confirm.ask", return_value=True)
def test_handle_no_version_raises(
    mock_confirm,
    mock_run_changelog,
    mock_has_head,
    tmp_path: Path,
) -> None:
    from usechange.changelog.cli.default import ChangelogResult

    mock_run_changelog.return_value = ChangelogResult(
        message="No version",
        content="",
        output_path=None,
        new_version=None,
        wrote_file=False,
        resolved_dir=str(tmp_path),
    )

    cmd = ReleaseCommand(app)
    try:
        cmd.handle(directory=str(tmp_path), yes=False, no_date=False, no_emojis=False)
        assert False, "Should have raised"
    except RuntimeError as e:
        assert "Unable to determine" in str(e)
