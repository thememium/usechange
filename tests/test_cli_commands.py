"""Tests for usechange.cli.commands — CLI command classes."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import typer

from usechange.cli.commands.changelog_command import ChangelogCommand
from usechange.cli.commands.github_release_command import GithubReleaseCommand

app = typer.Typer()


# --- ChangelogCommand ---

def test_changelog_command_signature() -> None:
    cmd = ChangelogCommand(app)
    assert cmd.signature() == "changelog"


def test_changelog_command_description() -> None:
    cmd = ChangelogCommand(app)
    assert "changelog" in cmd.description().lower()


def test_changelog_command_aliases() -> None:
    cmd = ChangelogCommand(app)
    assert "log" in cmd.aliases()


@patch("usechange.changelog.cli.default.run_changelog")
def test_changelog_command_handle_basic(mock_run) -> None:
    from usechange.changelog.cli.default import ChangelogResult
    mock_run.return_value = ChangelogResult(
        message="Generated", content="# Changelog\n", output_path=None, new_version="1.0.0", wrote_file=False, resolved_dir="/tmp"
    )
    cmd = ChangelogCommand(app)
    cmd.handle(
        repo_dir=None, from_ref=None, to_ref=None, directory=None, clean=False,
        output=None, write_output=False, no_output=True, no_authors=False,
        no_date=False, no_emojis=False, hide_author_email=False, bump=False,
        release_version=None, release=False, no_commit=False, no_tag=False,
        push=False, no_github=False, publish=False, publish_tag="latest",
        name_suffix=None, version_suffix=None, canary=None, major=False,
        minor=False, patch=False, premajor=None, preminor=None, prepatch=None,
        prerelease=None,
    )
    mock_run.assert_called_once()


@patch("usechange.changelog.cli.default.run_changelog")
def test_changelog_command_handle_with_output(mock_run) -> None:
    from usechange.changelog.cli.default import ChangelogResult
    mock_run.return_value = ChangelogResult(
        message="Generated", content="# Changelog\n", output_path="CHANGELOG.md", new_version="1.0.0", wrote_file=True, resolved_dir="/tmp"
    )
    cmd = ChangelogCommand(app)
    cmd.handle(
        repo_dir=None, from_ref=None, to_ref=None, directory=None, clean=False,
        output=None, write_output=False, no_output=False, no_authors=False,
        no_date=False, no_emojis=False, hide_author_email=False, bump=False,
        release_version=None, release=False, no_commit=False, no_tag=False,
        push=False, no_github=False, publish=False, publish_tag="latest",
        name_suffix=None, version_suffix=None, canary=None, major=False,
        minor=False, patch=False, premajor=None, preminor=None, prepatch=None,
        prerelease=None,
    )


@patch("usechange.changelog.cli.default.run_changelog")
def test_changelog_command_handle_no_content_shows_error(mock_run) -> None:
    from usechange.changelog.cli.default import ChangelogResult
    mock_run.return_value = ChangelogResult(
        message="Error occurred", content="", output_path=None, new_version=None, wrote_file=False, resolved_dir="/tmp"
    )
    cmd = ChangelogCommand(app)
    cmd.handle(
        repo_dir=None, from_ref=None, to_ref=None, directory=None, clean=False,
        output=None, write_output=False, no_output=True, no_authors=False,
        no_date=False, no_emojis=False, hide_author_email=False, bump=False,
        release_version=None, release=False, no_commit=False, no_tag=False,
        push=False, no_github=False, publish=False, publish_tag="latest",
        name_suffix=None, version_suffix=None, canary=None, major=False,
        minor=False, patch=False, premajor=None, preminor=None, prepatch=None,
        prerelease=None,
    )


@patch("usechange.changelog.cli.default.run_changelog")
def test_changelog_command_handle_message_only(mock_run) -> None:
    from usechange.changelog.cli.default import ChangelogResult
    mock_run.return_value = ChangelogResult(
        message="Done", content="", output_path=None, new_version="1.0.0", wrote_file=False, resolved_dir="/tmp"
    )
    cmd = ChangelogCommand(app)
    cmd.handle(
        repo_dir=None, from_ref=None, to_ref=None, directory=None, clean=False,
        output=None, write_output=False, no_output=True, no_authors=False,
        no_date=False, no_emojis=False, hide_author_email=False, bump=False,
        release_version=None, release=False, no_commit=False, no_tag=False,
        push=False, no_github=False, publish=False, publish_tag="latest",
        name_suffix=None, version_suffix=None, canary=None, major=False,
        minor=False, patch=False, premajor=None, preminor=None, prepatch=None,
        prerelease=None,
    )


# --- GithubReleaseCommand ---

def test_github_release_command_signature() -> None:
    cmd = GithubReleaseCommand(app)
    assert cmd.signature() == "github release"


def test_github_release_command_description() -> None:
    cmd = GithubReleaseCommand(app)
    assert "github" in cmd.description().lower()


def test_github_release_command_aliases() -> None:
    cmd = GithubReleaseCommand(app)
    assert "gh release" in cmd.aliases()


@patch("usechange.changelog.cli.gh_release.run_github_release")
def test_github_release_command_handle(mock_run) -> None:
    from usechange.changelog.cli.gh_release import GhReleaseResult
    mock_run.return_value = GhReleaseResult(message="Synced v1.0.0")
    cmd = GithubReleaseCommand(app)
    cmd.handle(versions=None, directory=None, token=None)
    mock_run.assert_called_once()
