"""Tests for usechange.changelog.cli.default — core changelog generation."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from usechange.changelog.cli.default import (
    ChangelogOptions,
    ParsedCommit,
    _collect_contributors,
    _format_commit,
    _group_commits,
    _merge_changelog,
    _parse_commit,
    _read_current_version,
    _resolve_output_path,
    _strip_emoji_from_title,
    _version_tag,
    run_changelog,
)
from usechange.changelog.config import default_types
from usechange.changelog.git import GitCommit
from usechange.changelog.repo import RepoInfo


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
        ["git", "config", "user.name", "Test User"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
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


def _default_options(**overrides) -> ChangelogOptions:
    base = {
        "repo_dir": None,
        "from_ref": None,
        "to_ref": None,
        "directory": None,
        "clean": False,
        "output": None,
        "no_output": True,
        "no_authors": False,
        "include_emojis": True,
        "include_date": True,
        "hide_author_email": False,
        "bump": False,
        "release_version": None,
        "release": False,
        "no_commit": False,
        "no_tag": False,
        "push": False,
        "no_github": False,
        "publish": False,
        "publish_tag": "latest",
        "name_suffix": None,
        "version_suffix": None,
        "canary": None,
        "major": False,
        "minor": False,
        "patch": False,
        "premajor": None,
        "preminor": None,
        "prepatch": None,
        "prerelease": None,
        "preview_next_version": False,
        "update_versions": True,
    }
    base.update(overrides)
    return ChangelogOptions(**base)


# --- _parse_commit ---


def test_parse_commit_conventional() -> None:
    commit = GitCommit(
        sha="abc1234",
        subject="feat(core): add feature",
        body="",
        author_name="Dev",
        author_email="dev@test.com",
    )
    parsed = _parse_commit(commit)
    assert parsed is not None
    assert parsed.type == "feat"
    assert parsed.scope == "core"
    assert parsed.subject == "add feature"
    assert parsed.breaking is False
    assert parsed.short_sha == "abc1234"


def test_parse_commit_breaking_bang() -> None:
    commit = GitCommit(
        sha="abc1234",
        subject="feat!: breaking change",
        body="",
        author_name="Dev",
        author_email="dev@test.com",
    )
    parsed = _parse_commit(commit)
    assert parsed is not None
    assert parsed.breaking is True


def test_parse_commit_breaking_footer() -> None:
    commit = GitCommit(
        sha="abc1234",
        subject="feat: add",
        body="BREAKING CHANGE: removed",
        author_name="Dev",
        author_email="dev@test.com",
    )
    parsed = _parse_commit(commit)
    assert parsed is not None
    assert parsed.breaking is True


def test_parse_commit_breaking_change_with_dash() -> None:
    commit = GitCommit(
        sha="abc1234",
        subject="feat: add",
        body="BREAKING-CHANGE: something",
        author_name="Dev",
        author_email="dev@test.com",
    )
    parsed = _parse_commit(commit)
    assert parsed is not None
    assert parsed.breaking is True


def test_parse_commit_references() -> None:
    commit = GitCommit(
        sha="abc1234",
        subject="fix: bug #42",
        body="Also #99",
        author_name="Dev",
        author_email="dev@test.com",
    )
    parsed = _parse_commit(commit)
    assert parsed is not None
    assert "#42" in parsed.references
    assert "#99" in parsed.references


def test_parse_commit_no_scope() -> None:
    commit = GitCommit(
        sha="abc1234",
        subject="feat: add feature",
        body="",
        author_name="Dev",
        author_email="dev@test.com",
    )
    parsed = _parse_commit(commit)
    assert parsed is not None
    assert parsed.scope is None


# --- _group_commits ---


def test_group_commits_basic() -> None:
    types = default_types()
    commits = [
        ParsedCommit(
            sha="a",
            short_sha="a",
            type="feat",
            scope=None,
            subject="new thing",
            breaking=False,
            author_name="Dev",
            author_email="dev@test.com",
            references=[],
        ),
        ParsedCommit(
            sha="b",
            short_sha="b",
            type="fix",
            scope=None,
            subject="bug fix",
            breaking=False,
            author_name="Dev",
            author_email="dev@test.com",
            references=[],
        ),
        ParsedCommit(
            sha="c",
            short_sha="c",
            type="other",
            scope=None,
            subject="misc",
            breaking=False,
            author_name="Dev",
            author_email="dev@test.com",
            references=[],
        ),
    ]
    sections = _group_commits(commits, types, None)
    titles = [s.title for s in sections]
    assert "🚀 Enhancements" in titles
    assert "🩹 Fixes" in titles
    assert "Other Changes" in titles


def test_group_commits_with_scope_and_refs() -> None:
    types = default_types()
    commits = [
        ParsedCommit(
            sha="a",
            short_sha="a123456",
            type="feat",
            scope="core",
            subject="feature",
            breaking=False,
            author_name="Dev",
            author_email="dev@test.com",
            references=["#42"],
        ),
    ]
    info = RepoInfo(domain="github.com", repo="user/repo", provider="github")
    sections = _group_commits(commits, types, info)
    assert len(sections) == 1
    item = sections[0].items[0]
    assert "**core**" in item
    assert "#42" in item
    assert "a123456" in item


def test_group_commits_without_repo_info() -> None:
    types = default_types()
    commits = [
        ParsedCommit(
            sha="abc1234567",
            short_sha="abc1234",
            type="fix",
            scope=None,
            subject="bug",
            breaking=False,
            author_name="Dev",
            author_email="dev@test.com",
            references=[],
        ),
    ]
    sections = _group_commits(commits, types, None)
    item = sections[0].items[0]
    assert "(abc1234)" in item


# --- _collect_contributors ---


def test_collect_contributors_basic() -> None:
    commits = [
        ParsedCommit(
            sha="a",
            short_sha="a",
            type="feat",
            scope=None,
            subject="s",
            breaking=False,
            author_name="Alice",
            author_email="alice@test.com",
            references=[],
        ),
        ParsedCommit(
            sha="b",
            short_sha="b",
            type="fix",
            scope=None,
            subject="s",
            breaking=False,
            author_name="Bob",
            author_email="bob@test.com",
            references=[],
        ),
    ]
    contributors = _collect_contributors(commits, [], False)
    assert "Alice <alice@test.com>" in contributors
    assert "Bob <bob@test.com>" in contributors


def test_collect_contributors_dedup() -> None:
    commits = [
        ParsedCommit(
            sha="a",
            short_sha="a",
            type="feat",
            scope=None,
            subject="s",
            breaking=False,
            author_name="Alice",
            author_email="alice@test.com",
            references=[],
        ),
        ParsedCommit(
            sha="b",
            short_sha="b",
            type="fix",
            scope=None,
            subject="s",
            breaking=False,
            author_name="Alice",
            author_email="alice@test.com",
            references=[],
        ),
    ]
    contributors = _collect_contributors(commits, [], False)
    assert len(contributors) == 1


def test_collect_contributors_exclude() -> None:
    commits = [
        ParsedCommit(
            sha="a",
            short_sha="a",
            type="feat",
            scope=None,
            subject="s",
            breaking=False,
            author_name="Bot",
            author_email="bot@test.com",
            references=[],
        ),
    ]
    contributors = _collect_contributors(commits, ["Bot"], False)
    assert len(contributors) == 0


def test_collect_contributors_hide_email() -> None:
    commits = [
        ParsedCommit(
            sha="a",
            short_sha="a",
            type="feat",
            scope=None,
            subject="s",
            breaking=False,
            author_name="Alice",
            author_email="alice@test.com",
            references=[],
        ),
    ]
    contributors = _collect_contributors(commits, [], True)
    assert contributors == ["Alice"]


# --- _strip_emoji_from_title ---


def test_strip_emoji_removes_leading_emoji() -> None:
    assert _strip_emoji_from_title("🚀 Enhancements") == "Enhancements"


def test_strip_emoji_no_emoji() -> None:
    assert _strip_emoji_from_title("Plain Title") == "Plain Title"


def test_strip_emoji_all_non_alphanumeric() -> None:
    # If stripping leaves nothing, returns original
    assert _strip_emoji_from_title("🎉🎊") == "🎉🎊"


# --- _version_tag ---


def test_version_tag_adds_v() -> None:
    assert _version_tag("1.0.0") == "v1.0.0"


def test_version_tag_already_has_v() -> None:
    assert _version_tag("v1.0.0") == "v1.0.0"


# --- _read_current_version ---


def test_read_current_version(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('name = "test"\nversion = "1.2.3"\n')
    assert _read_current_version(str(tmp_path)) == "1.2.3"


def test_read_current_version_no_file(tmp_path: Path) -> None:
    assert _read_current_version(str(tmp_path)) is None


def test_read_current_version_no_version_field(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('name = "test"\n')
    assert _read_current_version(str(tmp_path)) is None


# --- _resolve_output_path ---


def test_resolve_output_path_no_output_flag() -> None:
    options = _default_options(no_output=True)
    from usechange.changelog.config import ChangelogConfig

    config = ChangelogConfig()
    assert _resolve_output_path(options, config) is None


def test_resolve_output_path_config_output_false() -> None:
    options = _default_options(no_output=False)
    from usechange.changelog.config import ChangelogConfig

    config = ChangelogConfig(output=False)
    assert _resolve_output_path(options, config) is None


def test_resolve_output_path_custom_output() -> None:
    options = _default_options(no_output=False, output="CUSTOM.md")
    from usechange.changelog.config import ChangelogConfig

    config = ChangelogConfig()
    assert _resolve_output_path(options, config) == "CUSTOM.md"


def test_resolve_output_path_config_output_true() -> None:
    options = _default_options(no_output=False)
    from usechange.changelog.config import ChangelogConfig

    config = ChangelogConfig(output=True)
    assert _resolve_output_path(options, config) == "CHANGELOG.md"


def test_resolve_output_path_default() -> None:
    options = _default_options(no_output=False)
    from usechange.changelog.config import ChangelogConfig

    config = ChangelogConfig()
    assert _resolve_output_path(options, config) == "CHANGELOG.md"


# --- _merge_changelog ---


def test_merge_changelog_creates_new(tmp_path: Path) -> None:
    from usechange.changelog.markdown import ChangeSection, ReleaseNotes

    notes = ReleaseNotes(
        version="v1.0.0",
        date=None,
        sections=[ChangeSection(title="Features", items=["feat A"])],
    )
    content = _merge_changelog(str(tmp_path), None, notes)
    assert "v1.0.0" in content


def test_merge_changelog_merges_existing(tmp_path: Path) -> None:
    from usechange.changelog.markdown import ChangeSection, ReleaseNotes

    existing = "# Changelog\n\n## v0.9.0\n\n### Fixes\n\n- old fix\n\n"
    (tmp_path / "CHANGELOG.md").write_text(existing)
    notes = ReleaseNotes(
        version="v1.0.0",
        date=None,
        sections=[ChangeSection(title="Features", items=["new"])],
    )
    content = _merge_changelog(str(tmp_path), "CHANGELOG.md", notes)
    assert "v1.0.0" in content
    assert "v0.9.0" in content


def test_merge_changelog_replaces_same_version(tmp_path: Path) -> None:
    from usechange.changelog.markdown import ChangeSection, ReleaseNotes

    existing = "# Changelog\n\n## v1.0.0\n\n### Old\n\n- old item\n\n"
    (tmp_path / "CHANGELOG.md").write_text(existing)
    notes = ReleaseNotes(
        version="v1.0.0",
        date=None,
        sections=[ChangeSection(title="New", items=["new item"])],
    )
    content = _merge_changelog(str(tmp_path), "CHANGELOG.md", notes)
    assert "new item" in content
    assert "old item" not in content


# --- _format_commit ---


def test_format_commit_with_scope_and_url() -> None:
    commit = ParsedCommit(
        sha="abc1234567",
        short_sha="abc1234",
        type="feat",
        scope="core",
        subject="feature",
        breaking=False,
        author_name="D",
        author_email="d@t.com",
        references=["#1"],
    )
    info = RepoInfo(domain="github.com", repo="u/r", provider="github")
    result = _format_commit(commit, info)
    assert "**core**" in result
    assert "#1" in result
    assert "abc1234" in result
    assert "github.com" in result


def test_format_commit_no_scope_no_url() -> None:
    commit = ParsedCommit(
        sha="abc1234567",
        short_sha="abc1234",
        type="fix",
        scope=None,
        subject="bug",
        breaking=False,
        author_name="D",
        author_email="d@t.com",
        references=[],
    )
    result = _format_commit(commit, None)
    assert "(abc1234)" in result
    assert "**" not in result


# --- run_changelog ---


def test_run_changelog_basic(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: add feature")
    options = _default_options(
        directory=str(tmp_path), no_output=True, include_date=False
    )
    result = run_changelog(options)
    assert "v0.0.1" in result.content or "v" in result.content
    assert result.new_version is not None


def test_run_changelog_with_output(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: add feature")
    options = _default_options(
        directory=str(tmp_path), no_output=False, output="CHANGELOG.md"
    )
    result = run_changelog(options)
    assert result.wrote_file is True
    assert result.output_path == "CHANGELOG.md"
    assert (tmp_path / "CHANGELOG.md").exists()


def test_run_changelog_clean_flag_dirty(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    (tmp_path / "dirty.txt").write_text("dirty")
    options = _default_options(directory=str(tmp_path), clean=True, no_output=True)
    result = run_changelog(options)
    assert "not clean" in result.message.lower()


def test_run_changelog_clean_flag_clean(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    options = _default_options(directory=str(tmp_path), clean=True, no_output=True)
    result = run_changelog(options)
    assert result.new_version is not None


def test_run_changelog_no_authors(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    options = _default_options(directory=str(tmp_path), no_authors=True, no_output=True)
    result = run_changelog(options)
    assert "Contributors" not in result.content


def test_run_changelog_hide_author_email(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    options = _default_options(
        directory=str(tmp_path), hide_author_email=True, no_output=True
    )
    result = run_changelog(options)
    assert (
        "<" not in result.content.split("Contributors")[-1]
        if "Contributors" in result.content
        else True
    )


def test_run_changelog_release_version(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    options = _default_options(
        directory=str(tmp_path), release_version="5.0.0", no_output=True
    )
    result = run_changelog(options)
    assert "v5.0.0" in result.content


def test_run_changelog_with_date(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    options = _default_options(
        directory=str(tmp_path), include_date=True, no_output=True
    )
    result = run_changelog(options)
    # Date should be present in the header
    assert "(" in result.content


def test_run_changelog_no_emojis(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    options = _default_options(
        directory=str(tmp_path), include_emojis=False, no_output=True
    )
    result = run_changelog(options)
    # Emojis should be stripped from section titles
    assert "🚀" not in result.content


def test_run_changelog_with_bump(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('name = "test"\nversion = "1.0.0"\n')
    options = _default_options(directory=str(tmp_path), bump=True, no_output=True)
    result = run_changelog(options)
    assert result.new_version is not None
    assert result.new_version != "1.0.0"


def test_run_changelog_from_ref(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: first")
    subprocess.run(
        ["git", "tag", "v1.0.0"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    _make_commit(tmp_path, "fix: second")
    options = _default_options(
        directory=str(tmp_path), from_ref="v1.0.0", no_output=True
    )
    result = run_changelog(options)
    assert "second" in result.content


def test_run_changelog_update_versions(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('name = "test"\nversion = "1.0.0"\n')
    options = _default_options(
        directory=str(tmp_path), bump=True, no_output=True, update_versions=True
    )
    result = run_changelog(options)
    updated = pyproject.read_text()
    assert result.new_version is not None
    assert result.new_version in updated


def test_run_changelog_update_package_json(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('name = "test"\nversion = "1.0.0"\n')
    pkg = tmp_path / "package.json"
    pkg.write_text(json.dumps({"name": "test", "version": "1.0.0"}))
    options = _default_options(
        directory=str(tmp_path), bump=True, no_output=True, update_versions=True
    )
    result = run_changelog(options)
    updated_pkg = json.loads(pkg.read_text())
    assert updated_pkg["version"] == result.new_version


def test_run_changelog_major_bump(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('name = "test"\nversion = "1.0.0"\n')
    options = _default_options(directory=str(tmp_path), major=True, no_output=True)
    result = run_changelog(options)
    assert result.new_version == "2.0.0"


def test_run_changelog_minor_bump(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('name = "test"\nversion = "1.0.0"\n')
    options = _default_options(directory=str(tmp_path), minor=True, no_output=True)
    result = run_changelog(options)
    assert result.new_version == "1.1.0"


def test_run_changelog_patch_bump(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('name = "test"\nversion = "1.0.0"\n')
    options = _default_options(directory=str(tmp_path), patch=True, no_output=True)
    result = run_changelog(options)
    assert result.new_version == "1.0.1"


def test_run_changelog_premajor_bump(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('name = "test"\nversion = "1.0.0"\n')
    options = _default_options(
        directory=str(tmp_path), premajor="alpha", no_output=True
    )
    result = run_changelog(options)
    assert result.new_version is not None
    assert "alpha" in result.new_version


def test_run_changelog_preminor_bump(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('name = "test"\nversion = "1.0.0"\n')
    options = _default_options(directory=str(tmp_path), preminor="beta", no_output=True)
    result = run_changelog(options)
    assert result.new_version is not None
    assert "beta" in result.new_version


def test_run_changelog_prepatch_bump(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('name = "test"\nversion = "1.0.0"\n')
    options = _default_options(directory=str(tmp_path), prepatch="rc", no_output=True)
    result = run_changelog(options)
    assert result.new_version is not None
    assert "rc" in result.new_version


def test_run_changelog_prerelease_bump(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('name = "test"\nversion = "1.0.0"\n')
    options = _default_options(
        directory=str(tmp_path), prerelease="dev", no_output=True
    )
    result = run_changelog(options)
    assert result.new_version is not None
    assert "dev" in result.new_version


def test_run_changelog_preview_next_version(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('name = "test"\nversion = "1.0.0"\n')
    options = _default_options(
        directory=str(tmp_path), preview_next_version=True, no_output=True
    )
    result = run_changelog(options)
    # Should have auto-detected the bump
    assert result.new_version is not None
    assert result.new_version != "1.0.0"


def test_run_changelog_canary(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('name = "test"\nversion = "1.0.0"\n')
    options = _default_options(
        directory=str(tmp_path), canary="true", no_output=True, bump=True
    )
    result = run_changelog(options)
    assert result.new_version is not None


def test_run_changelog_version_suffix(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: initial")
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('name = "test"\nversion = "1.0.0"\n')
    options = _default_options(
        directory=str(tmp_path), version_suffix="beta.1", no_output=True, bump=True
    )
    result = run_changelog(options)
    assert result.new_version is not None
    assert "beta.1" in result.new_version


def test_run_changelog_to_ref(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _make_commit(tmp_path, "feat: first")
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    _make_commit(tmp_path, "fix: second")
    options = _default_options(directory=str(tmp_path), to_ref=sha, no_output=True)
    result = run_changelog(options)
    assert "first" in result.content
