"""Tests for usechange.changelog.github — GitHub API integration."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from usechange.changelog.github import (
    GitHubReleaseRequest,
    _load_gh_token,
    _normalize_tag,
    _request_json,
    sync_release,
)

# --- _normalize_tag ---


def test_normalize_tag_adds_v_prefix() -> None:
    assert _normalize_tag("1.0.0") == "v1.0.0"


def test_normalize_tag_already_has_v() -> None:
    assert _normalize_tag("v1.0.0") == "v1.0.0"


# --- _load_gh_token ---


def test_load_gh_token_no_file(tmp_path: Path) -> None:
    with patch.object(Path, "home", return_value=tmp_path):
        assert _load_gh_token() is None


def test_load_gh_token_with_token(tmp_path: Path) -> None:
    gh_dir = tmp_path / ".config" / "gh"
    gh_dir.mkdir(parents=True)
    hosts = gh_dir / "hosts.yml"
    hosts.write_text("github.com:\n    oauth_token: ghp_testtoken123\n")
    with patch.object(Path, "home", return_value=tmp_path):
        token = _load_gh_token()
    assert token == "ghp_testtoken123"


def test_load_gh_token_with_quoted_token(tmp_path: Path) -> None:
    gh_dir = tmp_path / ".config" / "gh"
    gh_dir.mkdir(parents=True)
    hosts = gh_dir / "hosts.yml"
    hosts.write_text('github.com:\n    oauth_token: "ghp_quoted"\n')
    with patch.object(Path, "home", return_value=tmp_path):
        token = _load_gh_token()
    assert token == "ghp_quoted"


def test_load_gh_token_wrong_section(tmp_path: Path) -> None:
    gh_dir = tmp_path / ".config" / "gh"
    gh_dir.mkdir(parents=True)
    hosts = gh_dir / "hosts.yml"
    hosts.write_text("gitlab.com:\n    oauth_token: glpat_test\n")
    with patch.object(Path, "home", return_value=tmp_path):
        assert _load_gh_token() is None


# --- sync_release ---


def test_sync_release_no_repo_raises() -> None:
    request = GitHubReleaseRequest(version="1.0.0", body="body", token="tok", repo=None)
    try:
        sync_release(request)
        assert False, "Should have raised"
    except RuntimeError as e:
        assert "Missing repository" in str(e)


def test_sync_release_no_token_raises() -> None:
    request = GitHubReleaseRequest(
        version="1.0.0", body="body", token=None, repo="user/repo"
    )
    with (
        patch.dict("os.environ", {}, clear=True),
        patch.object(Path, "home", return_value=Path("/nonexistent")),
    ):
        try:
            sync_release(request)
            assert False, "Should have raised"
        except RuntimeError as e:
            assert "Missing GitHub token" in str(e)


@patch("usechange.changelog.github._request_json")
def test_sync_release_create_new(mock_request: MagicMock) -> None:
    # First call (check existing) returns None, second call (create) returns something
    mock_request.side_effect = [None, {"id": 1}]
    request = GitHubReleaseRequest(
        version="1.0.0", body="release body", token="tok", repo="user/repo"
    )
    result = sync_release(request)
    assert result is True
    assert mock_request.call_count == 2
    # Verify the POST call
    create_call = mock_request.call_args_list[1]
    assert create_call[0][0] == "https://api.github.com/repos/user/repo/releases"
    assert create_call[1]["method"] == "POST"


@patch("usechange.changelog.github._request_json")
def test_sync_release_update_existing(mock_request: MagicMock) -> None:
    # First call returns existing release with id
    mock_request.return_value = {"id": 42}
    request = GitHubReleaseRequest(
        version="1.0.0", body="updated body", token="tok", repo="user/repo"
    )
    result = sync_release(request)
    assert result is True
    # Second call should be PATCH
    patch_call = mock_request.call_args_list[1]
    assert patch_call[0][0] == "https://api.github.com/repos/user/repo/releases/42"
    assert patch_call[1]["method"] == "PATCH"


@patch("usechange.changelog.github._request_json")
def test_sync_release_prerelease(mock_request: MagicMock) -> None:
    mock_request.side_effect = [None, {"id": 1}]
    request = GitHubReleaseRequest(
        version="1.0.0-alpha.1", body="body", token="tok", repo="user/repo"
    )
    sync_release(request)
    create_call = mock_request.call_args_list[1]
    payload = create_call[1]["payload"]
    assert payload["prerelease"] is True


@patch("usechange.changelog.github._request_json")
def test_sync_release_not_prerelease(mock_request: MagicMock) -> None:
    mock_request.side_effect = [None, {"id": 1}]
    request = GitHubReleaseRequest(
        version="1.0.0", body="body", token="tok", repo="user/repo"
    )
    sync_release(request)
    create_call = mock_request.call_args_list[1]
    payload = create_call[1]["payload"]
    assert payload["prerelease"] is False


# --- _request_json ---


@patch("usechange.changelog.github.urllib.request.urlopen")
def test_request_json_success(mock_urlopen: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"key": "value"}).encode()
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = mock_response

    result = _request_json("https://api.github.com/repos/user/repo", "token")
    assert result == {"key": "value"}


@patch("usechange.changelog.github.urllib.request.urlopen")
def test_request_json_empty_body(mock_urlopen: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.read.return_value = b""
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = mock_response

    result = _request_json("https://api.example.com", None)
    assert result is None


@patch("usechange.changelog.github.urllib.request.urlopen")
def test_request_json_404_returns_none(mock_urlopen: MagicMock) -> None:
    import urllib.error
    from http.client import HTTPMessage

    mock_fp = MagicMock()
    mock_fp.read.return_value = b"Not Found"
    mock_urlopen.side_effect = urllib.error.HTTPError(
        url="https://api.github.com",
        code=404,
        msg="Not Found",
        hdrs=HTTPMessage(),
        fp=mock_fp,
    )

    result = _request_json(
        "https://api.github.com/repos/user/repo/releases/tags/v1.0.0", "token"
    )
    assert result is None


@patch("usechange.changelog.github.urllib.request.urlopen")
def test_request_json_other_http_error_raises(mock_urlopen: MagicMock) -> None:
    import urllib.error
    from http.client import HTTPMessage

    mock_fp = MagicMock()
    mock_fp.read.return_value = b"Internal Server Error"
    error = urllib.error.HTTPError(
        url="https://api.github.com",
        code=500,
        msg="Server Error",
        hdrs=HTTPMessage(),
        fp=mock_fp,
    )
    mock_urlopen.side_effect = error

    try:
        _request_json("https://api.github.com", "token")
        assert False, "Should have raised"
    except RuntimeError:
        pass


@patch("usechange.changelog.github.urllib.request.urlopen")
def test_request_json_with_post_payload(mock_urlopen: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"id": 1}).encode()
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = mock_response

    result = _request_json(
        "https://api.github.com", "tok", method="POST", payload={"name": "test"}
    )
    assert result == {"id": 1}


@patch("usechange.changelog.github.urllib.request.urlopen")
def test_request_json_no_token(mock_urlopen: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"ok":true}'
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = mock_response

    result = _request_json("https://api.github.com", None)
    assert result == {"ok": True}
