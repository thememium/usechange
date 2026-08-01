"""Tests for usechange.changelog.git — git operations."""

from __future__ import annotations

import subprocess
from pathlib import Path

from usechange.changelog.git import (
    _run_git,
    get_current_ref,
    get_default_branch,
    get_latest_tag,
    get_log,
    get_previous_tag,
    get_repo_root,
    get_short_ref,
    has_head,
    is_clean,
)


def _init_repo(path: Path) -> None:
    subprocess.run(
        ["git", "init"], cwd=path, check=True, capture_output=True, text=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )


_commit_counter = 0


def _make_commit(path: Path, message: str, filename: str = "file.txt") -> None:
    global _commit_counter
    _commit_counter += 1
    (path / filename).write_text(f"content {_commit_counter}\n")
    subprocess.run(
        ["git", "add", filename], cwd=path, check=True, capture_output=True, text=True
    )
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Test User",
            "-c",
            "user.email=test@test.com",
            "commit",
            "-m",
            message,
            "-m",
            f"Commit body {_commit_counter}",
        ],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )


def _make_tag(path: Path, tag: str) -> None:
    subprocess.run(
        ["git", "tag", tag], cwd=path, check=True, capture_output=True, text=True
    )


# --- _run_git ---


def test_run_git_raises_on_failure(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    try:
        _run_git(str(tmp_path), ["describe", "--tags", "--abbrev=0"])
        assert False, "Should have raised"
    except RuntimeError:
        pass


def test_run_git_returns_output(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    result = _run_git(str(tmp_path), ["rev-parse", "HEAD"])
    assert len(result) == 40  # SHA is 40 hex chars


# --- get_repo_root ---


def test_get_repo_root_in_repo(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    root = get_repo_root(str(tmp_path))
    assert root is not None
    assert root == str(tmp_path)


def test_get_repo_root_outside_repo(tmp_path: Path) -> None:
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    assert get_repo_root(str(subdir)) is None


# --- has_head ---


def test_has_head_empty_repo(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    assert has_head(str(tmp_path)) is False


def test_has_head_with_commit(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    assert has_head(str(tmp_path)) is True


# --- is_clean ---


def test_is_clean_true(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    assert is_clean(str(tmp_path)) is True


def test_is_clean_false_with_untracked(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    (tmp_path / "untracked.txt").write_text("hello")
    assert is_clean(str(tmp_path)) is False


# --- get_latest_tag ---


def test_get_latest_tag_with_tag(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: first")
    _make_tag(tmp_path, "v1.0.0")
    assert get_latest_tag(str(tmp_path)) == "v1.0.0"


def test_get_latest_tag_no_tags(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: first")
    assert get_latest_tag(str(tmp_path)) is None


# --- get_previous_tag ---


def test_get_previous_tag(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: first")
    _make_tag(tmp_path, "v1.0.0")
    _make_commit(tmp_path, "feat: second")
    _make_tag(tmp_path, "v2.0.0")
    prev = get_previous_tag(str(tmp_path), "v2.0.0")
    assert prev == "v1.0.0"


def test_get_previous_tag_no_previous(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: first")
    _make_tag(tmp_path, "v1.0.0")
    prev = get_previous_tag(str(tmp_path), "v1.0.0")
    assert prev is None


# --- get_current_ref / get_short_ref ---


def test_get_current_ref(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    ref = get_current_ref(str(tmp_path))
    assert len(ref) == 40


def test_get_short_ref(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    ref = get_short_ref(str(tmp_path))
    assert len(ref) == 7


# --- get_log ---


def test_get_log_full(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: first")
    _make_commit(tmp_path, "fix: second")
    commits = get_log(str(tmp_path), None, None)
    assert len(commits) == 2
    assert commits[0].subject == "fix: second"  # newest first
    assert commits[1].subject == "feat: first"


def test_get_log_with_range(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: first")
    _make_tag(tmp_path, "v1.0.0")
    _make_commit(tmp_path, "fix: second")
    commits = get_log(str(tmp_path), "v1.0.0", "HEAD")
    assert len(commits) == 1
    assert commits[0].subject == "fix: second"


def test_get_log_from_ref_only(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: first")
    _make_tag(tmp_path, "v1.0.0")
    _make_commit(tmp_path, "fix: second")
    commits = get_log(str(tmp_path), "v1.0.0", None)
    assert len(commits) == 1


def test_get_log_to_ref_only(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: first")
    sha = get_current_ref(str(tmp_path))
    _make_commit(tmp_path, "fix: second")
    commits = get_log(str(tmp_path), None, sha)
    assert len(commits) == 1
    assert commits[0].subject == "feat: first"


def test_get_log_body_and_references(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    (tmp_path / "file.txt").write_text("content")
    subprocess.run(
        ["git", "add", "file.txt"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    # Commit with body containing a BREAKING CHANGE and issue ref
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Test User",
            "-c",
            "user.email=test@test.com",
            "commit",
            "-m",
            "feat(api)!: new endpoint\n\nBREAKING CHANGE: removed old\n\nFixes #42",
        ],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    commits = get_log(str(tmp_path), None, None)
    assert len(commits) == 1
    assert "BREAKING CHANGE" in commits[0].body


# --- get_default_branch ---


def test_get_default_branch_no_remote(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    assert get_default_branch(str(tmp_path)) is None


def test_get_default_branch_with_remote(tmp_path: Path) -> None:
    bare = tmp_path / "bare.git"
    bare.mkdir()
    subprocess.run(
        ["git", "init", "--bare", str(bare)],
        check=True,
        capture_output=True,
        text=True,
    )
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    subprocess.run(
        ["git", "remote", "add", "origin", str(bare)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "push", "-u", "origin", "master"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "remote", "set-head", "origin", "master"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    branch = get_default_branch(str(tmp_path))
    assert branch == "master"
