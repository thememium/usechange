from __future__ import annotations

import subprocess
from pathlib import Path

from usechange.changelog import git
from usechange.changelog.cli.default import ChangelogOptions, run_changelog


def _init_repo(path: Path) -> None:
    subprocess.run(
        ["git", "init"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )


def _commit_file(path: Path, message: str) -> None:
    target = path / "README.md"
    target.write_text("test\n")
    subprocess.run(
        ["git", "add", "README.md"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Test User",
            "-c",
            "user.email=test@example.com",
            "commit",
            "-m",
            message,
        ],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )


def test_has_head_false_in_empty_repo(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    assert git.has_head(str(tmp_path)) is False


def test_has_head_true_after_commit(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _commit_file(tmp_path, "feat: initial commit")
    assert git.has_head(str(tmp_path)) is True


def test_run_changelog_missing_head(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    options = ChangelogOptions(
        repo_dir=None,
        from_ref=None,
        to_ref=None,
        directory=str(tmp_path),
        clean=False,
        output=None,
        no_output=True,
        no_authors=False,
        include_emojis=True,
        include_date=True,
        hide_author_email=False,
        bump=False,
        release_version=None,
        release=False,
        no_commit=False,
        no_tag=False,
        push=False,
        no_github=False,
        publish=False,
        publish_tag="latest",
        name_suffix=None,
        version_suffix=None,
        canary=None,
        major=False,
        minor=False,
        patch=False,
        premajor=None,
        preminor=None,
        prepatch=None,
        prerelease=None,
        preview_next_version=False,
        update_versions=True,
    )
    result = run_changelog(options)
    assert "no commits" in result.message.lower()
    assert result.content == ""
    assert result.output_path is None
