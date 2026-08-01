"""Tests for usechange.changelog.repo — repo URL parsing and resolution."""

from __future__ import annotations

import subprocess
from pathlib import Path

from usechange.changelog.config import RepoConfig
from usechange.changelog.repo import (
    RepoInfo,
    _normalize_remote_url,
    _parse_repo,
    commit_url,
    compare_url,
    resolve_repo,
)

# --- _normalize_remote_url ---


def test_normalize_ssh_url() -> None:
    assert (
        _normalize_remote_url("git@github.com:user/repo.git")
        == "https://github.com/user/repo"
    )


def test_normalize_https_url() -> None:
    assert (
        _normalize_remote_url("https://github.com/user/repo.git")
        == "https://github.com/user/repo"
    )


def test_normalize_http_to_https() -> None:
    assert (
        _normalize_remote_url("http://github.com/user/repo")
        == "https://github.com/user/repo"
    )


def test_normalize_empty_string() -> None:
    assert _normalize_remote_url("") is None


def test_normalize_whitespace_only() -> None:
    assert _normalize_remote_url("   ") is None


def test_normalize_plain_https_no_suffix() -> None:
    assert (
        _normalize_remote_url("https://gitlab.com/org/project")
        == "https://gitlab.com/org/project"
    )


# --- _parse_repo ---


def test_parse_github_ssh() -> None:
    info = _parse_repo("git@github.com:user/repo.git")
    assert info is not None
    assert info.domain == "github.com"
    assert info.repo == "user/repo"
    assert info.provider == "github"


def test_parse_gitlab_https() -> None:
    info = _parse_repo("https://gitlab.com/org/project.git")
    assert info is not None
    assert info.domain == "gitlab.com"
    assert info.repo == "org/project"
    assert info.provider == "gitlab"


def test_parse_bitbucket() -> None:
    info = _parse_repo("https://bitbucket.org/team/repo")
    assert info is not None
    assert info.provider == "bitbucket"


def test_parse_unknown_provider() -> None:
    info = _parse_repo("https://custom-git.example.com/a/b")
    assert info is not None
    assert info.domain == "custom-git.example.com"
    assert info.repo == "a/b"
    assert info.provider is None


def test_parse_empty_string() -> None:
    assert _parse_repo("") is None


def test_parse_non_url() -> None:
    # A string that doesn't match https pattern after normalization
    info = _parse_repo("not-a-url")
    # _normalize_remote_url will return "not-a-url" which won't match https regex
    # so _parse_repo returns RepoInfo with domain=None, repo=normalized
    assert info is not None
    assert info.domain is None


# --- resolve_repo ---


def test_resolve_repo_with_repo_info() -> None:
    existing = RepoInfo(domain="github.com", repo="a/b", provider="github")
    assert resolve_repo(existing) is existing


def test_resolve_repo_with_repo_config() -> None:
    config = RepoConfig(domain="github.com", repo="a/b", provider="github")
    info = resolve_repo(config)
    assert info is not None
    assert info.domain == "github.com"
    assert info.repo == "a/b"
    assert info.provider == "github"


def test_resolve_repo_with_string() -> None:
    info = resolve_repo("git@github.com:user/repo.git")
    assert info is not None
    assert info.repo == "user/repo"


def test_resolve_repo_with_empty_string_falls_through() -> None:
    # Empty string is falsy, so it goes to directory check (None)
    result = resolve_repo("", directory=None)
    assert result is None


def test_resolve_repo_with_none() -> None:
    assert resolve_repo(None, directory=None) is None


def test_resolve_repo_with_directory(tmp_path: Path) -> None:
    subprocess.run(
        ["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True
    )
    subprocess.run(
        ["git", "remote", "add", "origin", "git@github.com:test-org/test-repo.git"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    info = resolve_repo(None, directory=str(tmp_path))
    assert info is not None
    assert info.repo == "test-org/test-repo"
    assert info.provider == "github"


def test_resolve_repo_directory_no_remote(tmp_path: Path) -> None:
    subprocess.run(
        ["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True
    )
    info = resolve_repo(None, directory=str(tmp_path))
    # No remote set, so git remote get-url origin will fail
    assert info is None


# --- commit_url / compare_url ---


def test_commit_url_with_valid_info() -> None:
    info = RepoInfo(domain="github.com", repo="user/repo", provider="github")
    assert commit_url(info, "abc123") == "https://github.com/user/repo/commit/abc123"


def test_commit_url_with_none_info() -> None:
    assert commit_url(None, "abc123") is None


def test_commit_url_with_missing_domain() -> None:
    info = RepoInfo(domain=None, repo="user/repo", provider=None)
    assert commit_url(info, "abc123") is None


def test_compare_url_with_valid_info() -> None:
    info = RepoInfo(domain="github.com", repo="user/repo", provider="github")
    assert (
        compare_url(info, "v1.0.0", "v2.0.0")
        == "https://github.com/user/repo/compare/v1.0.0...v2.0.0"
    )


def test_compare_url_with_none_info() -> None:
    assert compare_url(None, "v1.0.0", "v2.0.0") is None


def test_compare_url_with_missing_repo() -> None:
    info = RepoInfo(domain="github.com", repo=None, provider=None)
    assert compare_url(info, "a", "b") is None
