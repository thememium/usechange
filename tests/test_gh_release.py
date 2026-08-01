"""Tests for usechange.changelog.cli.gh_release — GitHub release CLI."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from usechange.changelog.cli.gh_release import (
    GhReleaseOptions,
    _load_changelog,
    _resolve_versions,
    run_github_release,
)
from usechange.changelog.markdown import ChangeSection, ReleaseNotes


# --- _resolve_versions ---

def test_resolve_versions_all() -> None:
    releases = [
        ReleaseNotes(version="v2.0.0", date=None, sections=[]),
        ReleaseNotes(version="v1.0.0", date=None, sections=[]),
    ]
    result = _resolve_versions(["all"], releases)
    assert len(result) == 2


def test_resolve_versions_specific() -> None:
    releases = [
        ReleaseNotes(version="v2.0.0", date=None, sections=[]),
        ReleaseNotes(version="v1.0.0", date=None, sections=[]),
    ]
    result = _resolve_versions(["v1.0.0"], releases)
    assert len(result) == 1
    assert result[0].version == "v1.0.0"


def test_resolve_versions_no_versions_returns_first() -> None:
    releases = [
        ReleaseNotes(version="v2.0.0", date=None, sections=[]),
        ReleaseNotes(version="v1.0.0", date=None, sections=[]),
    ]
    result = _resolve_versions(None, releases)
    assert len(result) == 1
    assert result[0].version == "v2.0.0"


def test_resolve_versions_no_match_raises() -> None:
    releases = [ReleaseNotes(version="v1.0.0", date=None, sections=[])]
    try:
        _resolve_versions(["v9.9.9"], releases)
        assert False, "Should have raised"
    except RuntimeError as e:
        assert "No matching" in str(e)


# --- _load_changelog ---

def test_load_changelog_local_file(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("# Changelog\n\n## v1.0.0\n\n### Features\n\n- Thing\n\n")
    content = _load_changelog(str(tmp_path))
    assert "v1.0.0" in content


@patch("usechange.changelog.cli.gh_release.resolve_repo")
@patch("usechange.changelog.cli.gh_release.git.get_default_branch")
@patch("usechange.changelog.cli.gh_release.urllib.request.urlopen")
def test_load_changelog_fetch_from_github(mock_urlopen, mock_branch, mock_repo, tmp_path: Path) -> None:
    from usechange.changelog.repo import RepoInfo
    mock_repo.return_value = RepoInfo(domain="github.com", repo="user/repo", provider="github")
    mock_branch.return_value = "main"
    mock_response = MagicMock()
    mock_response.read.return_value = b"# Changelog\n\n## v1.0.0\n"
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = mock_response

    content = _load_changelog(str(tmp_path))
    assert "v1.0.0" in content


@patch("usechange.changelog.cli.gh_release.resolve_repo")
def test_load_changelog_no_repo_raises(mock_repo, tmp_path: Path) -> None:
    mock_repo.return_value = None
    try:
        _load_changelog(str(tmp_path))
        assert False, "Should have raised"
    except RuntimeError as e:
        assert "Missing changelog" in str(e)


@patch("usechange.changelog.cli.gh_release.resolve_repo")
@patch("usechange.changelog.cli.gh_release.git.get_default_branch")
@patch("usechange.changelog.cli.gh_release.urllib.request.urlopen")
def test_load_changelog_github_404_raises(mock_urlopen, mock_branch, mock_repo, tmp_path: Path) -> None:
    import urllib.error
    from usechange.changelog.repo import RepoInfo
    mock_repo.return_value = RepoInfo(domain="github.com", repo="user/repo", provider="github")
    mock_branch.return_value = "main"
    mock_urlopen.side_effect = urllib.error.HTTPError(url="", code=404, msg="", hdrs=None, fp=None)
    try:
        _load_changelog(str(tmp_path))
        assert False, "Should have raised"
    except RuntimeError as e:
        assert "Unable to fetch" in str(e)


# --- run_github_release ---

@patch("usechange.changelog.cli.gh_release.sync_release")
@patch("usechange.changelog.cli.gh_release.resolve_repo")
def test_run_github_release_basic(mock_repo, mock_sync, tmp_path: Path) -> None:
    from usechange.changelog.repo import RepoInfo
    mock_repo.return_value = RepoInfo(domain="github.com", repo="user/repo", provider="github")
    mock_sync.return_value = True

    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("# Changelog\n\n## v1.0.0\n\n### Features\n\n- Thing\n\n")
    options = GhReleaseOptions(versions=None, directory=str(tmp_path), token="tok")
    result = run_github_release(options)
    assert "v1.0.0" in result.message
    mock_sync.assert_called_once()


@patch("usechange.changelog.cli.gh_release.sync_release")
@patch("usechange.changelog.cli.gh_release.resolve_repo")
def test_run_github_release_all(mock_repo, mock_sync, tmp_path: Path) -> None:
    from usechange.changelog.repo import RepoInfo
    mock_repo.return_value = RepoInfo(domain="github.com", repo="user/repo", provider="github")
    mock_sync.return_value = True

    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("# Changelog\n\n## v2.0.0\n\n- B\n\n## v1.0.0\n\n- A\n\n")
    options = GhReleaseOptions(versions=["all"], directory=str(tmp_path), token="tok")
    result = run_github_release(options)
    assert mock_sync.call_count == 2


def test_run_github_release_no_releases(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("# Changelog\n\n")
    options = GhReleaseOptions(versions=None, directory=str(tmp_path), token=None)
    result = run_github_release(options)
    assert "No releases" in result.message
