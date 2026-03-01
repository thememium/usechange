from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from dataclasses import replace
from pathlib import Path

from usecli import Argument, BaseCommand, Confirm, Option, console


class ReleaseCommand(BaseCommand):
    def signature(self) -> str:
        return "release"

    def description(self) -> str:
        return "Run release workflow using usechange changelog"

    def handle(
        self,
        repo_dir: str | None = Argument(
            None, help="Repository path (positional, legacy)"
        ),
        from_ref: str | None = Option(None, "--from", help="Start commit reference"),
        to_ref: str | None = Option(None, "--to", help="End commit reference"),
        directory: str | None = Option(None, "--dir", help="Path to a git repository"),
        clean: bool = Option(
            False, "--clean", is_flag=True, help="Ensure working directory is clean"
        ),
        output: str | None = Option(None, "--output", help="Changelog file to write"),
        write_output: bool = Option(
            True,
            "--write",
            is_flag=True,
            help="Write changelog to CHANGELOG.md",
        ),
        no_output: bool = Option(
            False, "--no-output", is_flag=True, help="Do not write a changelog file"
        ),
        no_authors: bool = Option(
            False, "--noAuthors", is_flag=True, help="Skip contributors section"
        ),
        yes: bool = Option(False, "--yes", "-y", help="Skip confirmation"),
        no_date: bool = Option(
            False, "--noDate", is_flag=True, help="Omit date from header"
        ),
        no_emojis: bool = Option(
            False, "--noEmojis", is_flag=True, help="Omit emojis from headers"
        ),
        hide_author_email: bool = Option(
            False,
            "--hideAuthorEmail",
            is_flag=True,
            help="Hide author email if no username is found",
        ),
        bump: bool = Option(
            False, "--bump", is_flag=True, help="Determine and update version"
        ),
        release_version: str | None = Option(
            None, "-r", help="Release as a specific version"
        ),
        release: bool = Option(
            False, "--release", is_flag=True, help="Bump, tag, and release"
        ),
        no_commit: bool = Option(
            False, "--no-commit", is_flag=True, help="Skip release commit"
        ),
        no_tag: bool = Option(False, "--no-tag", is_flag=True, help="Skip release tag"),
        push: bool = Option(
            False, "--push", is_flag=True, help="Push commits and tags"
        ),
        no_github: bool = Option(
            False, "--no-github", is_flag=True, help="Skip GitHub release sync"
        ),
        publish: bool = Option(
            False, "--publish", is_flag=True, help="Publish after generating"
        ),
        publish_tag: str = Option(
            "latest", "--publishTag", help="Publish with a custom tag"
        ),
        name_suffix: str | None = Option(
            None, "--nameSuffix", help="Append suffix to package name"
        ),
        version_suffix: str | None = Option(
            None, "--versionSuffix", help="Append suffix to version"
        ),
        canary: str | None = Option(
            None,
            "--canary",
            help="Shortcut for --bump and --versionSuffix",
        ),
        major: bool = Option(False, "--major", is_flag=True, help="Force major bump"),
        minor: bool = Option(False, "--minor", is_flag=True, help="Force minor bump"),
        patch: bool = Option(False, "--patch", is_flag=True, help="Force patch bump"),
        premajor: str | None = Option(None, "--premajor", help="Force premajor bump"),
        preminor: str | None = Option(None, "--preminor", help="Force preminor bump"),
        prepatch: str | None = Option(None, "--prepatch", help="Force prepatch bump"),
        prerelease: str | None = Option(
            None, "--prerelease", help="Force prerelease bump"
        ),
    ) -> None:
        _ensure_src_on_path()
        from usechange.changelog.cli.default import (
            ChangelogOptions,
            _resolve_config_from_options,
            _resolve_output_path,
            run_changelog,
        )

        if not yes and not Confirm.ask("Continue with release?", default=False):
            console.print("Release cancelled.")
            return

        resolved_dir = str(Path(directory or repo_dir or ".").resolve())
        effective_no_output = no_output or (output is None and not write_output)
        base_options = ChangelogOptions(
            repo_dir=repo_dir,
            from_ref=from_ref,
            to_ref=to_ref,
            directory=directory,
            clean=clean,
            output=output,
            no_output=effective_no_output,
            no_authors=no_authors,
            include_emojis=not no_emojis,
            include_date=not no_date,
            hide_author_email=hide_author_email,
            bump=bump,
            release_version=release_version,
            release=release,
            no_commit=no_commit,
            no_tag=no_tag,
            push=push,
            no_github=no_github,
            publish=publish,
            publish_tag=publish_tag,
            name_suffix=name_suffix,
            version_suffix=version_suffix,
            canary=canary,
            major=major,
            minor=minor,
            patch=patch,
            premajor=premajor,
            preminor=preminor,
            prepatch=prepatch,
            prerelease=prerelease,
            preview_next_version=True,
            update_versions=False,
        )
        config = _resolve_config_from_options(resolved_dir, base_options)
        output_path = _resolve_output_path(base_options, config)
        existing_versions = _load_existing_versions(resolved_dir, output_path)
        changelog_result = run_changelog(base_options)

        version = changelog_result.new_version
        if not version:
            raise RuntimeError("Unable to determine release version")

        next_version = _next_available_version(resolved_dir, version, existing_versions)
        if next_version != version:
            console.print(f"Version {version} exists. Bumping to {next_version}.")
            changelog_result = run_changelog(
                replace(base_options, release_version=next_version)
            )
            version = next_version

        tag_name = f"v{version}"

        _run(resolved_dir, ["uv", "version", version])
        _run(resolved_dir, ["uv", "sync"])
        _run(resolved_dir, ["uv", "lock"])

        notes = _extract_release_notes(changelog_result.content, tag_name)
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as handle:
            handle.write(notes)
            notes_file = handle.name

        if not no_commit:
            changelog_files = _resolve_changelog_files(resolved_dir, changelog_result)
            _run(
                resolved_dir,
                [
                    "git",
                    "add",
                    *changelog_files,
                    "pyproject.toml",
                    "uv.lock",
                ],
            )
            _run(resolved_dir, ["git", "commit", "-m", "chore(uv): update version"])
        if not no_tag:
            _run(resolved_dir, ["git", "tag", tag_name])
        if push:
            _run(resolved_dir, ["git", "push"])
            if not no_tag:
                _run(resolved_dir, ["git", "push", "origin", tag_name])
        if not no_github and not no_tag:
            _ensure_gh_ready(resolved_dir)
            target_sha = _run_capture(resolved_dir, ["git", "rev-parse", tag_name])
            target_ref, default_branch = _resolve_release_target(
                resolved_dir, target_sha
            )
            if target_ref and target_ref != target_sha:
                console.print(
                    "Local release commit not found on origin. "
                    f"Targeting {default_branch} for GitHub release. "
                    "Use --push to publish local commits and tags."
                )
            if _gh_release_exists(resolved_dir, tag_name):
                _run(
                    resolved_dir,
                    ["gh", "release", "edit", tag_name, "--notes-file", notes_file],
                )
            else:
                release_args = [
                    "gh",
                    "release",
                    "create",
                    tag_name,
                    "--notes-file",
                    notes_file,
                ]
                if target_ref:
                    release_args.extend(["--target", target_ref])
                _run(
                    resolved_dir,
                    release_args,
                )
        console.print(f"Release {version} completed.")


def _run(directory: str, args: list[str]) -> None:
    result = subprocess.run(
        args,
        cwd=directory,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        details = result.stderr.strip() or result.stdout.strip()
        suffix = f"\n{details}" if details else ""
        raise RuntimeError(f"Command failed: {' '.join(args)}{suffix}")


def _run_capture(directory: str, args: list[str]) -> str:
    result = subprocess.run(
        args,
        cwd=directory,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        details = result.stderr.strip() or result.stdout.strip()
        suffix = f"\n{details}" if details else ""
        raise RuntimeError(f"Command failed: {' '.join(args)}{suffix}")
    return result.stdout.strip()


def _ensure_gh_ready(directory: str) -> None:
    if not shutil.which("gh"):
        raise RuntimeError("GitHub CLI (gh) not found. Install gh or pass --no-github.")
    result = subprocess.run(
        ["gh", "auth", "status", "-h", "github.com"],
        cwd=directory,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        details = result.stderr.strip() or result.stdout.strip()
        suffix = f"\n{details}" if details else ""
        raise RuntimeError(
            "GitHub CLI is not authenticated. Run `gh auth login` or pass --no-github."
            + suffix
        )


def _extract_release_notes(changelog_content: str, tag_name: str) -> str:
    lines = changelog_content.splitlines()
    heading = f"## {tag_name}"
    start = None
    for idx, line in enumerate(lines):
        if line.strip().startswith(heading):
            start = idx
            break
    if start is None:
        raise RuntimeError(f"Missing changelog entry for {heading}")
    end = None
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("## "):
            end = idx
            break
    section = lines[start:end]
    return "\n".join(section).rstrip()


def _gh_release_exists(directory: str, tag_name: str) -> bool:
    result = subprocess.run(
        ["gh", "release", "view", tag_name],
        cwd=directory,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _remote_ref_exists(directory: str, ref_name: str) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--quiet", "--verify", f"refs/remotes/{ref_name}"],
        cwd=directory,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _commit_in_remote(directory: str, commit_sha: str, remote_ref: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit_sha, remote_ref],
        cwd=directory,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _resolve_release_target(
    directory: str, commit_sha: str
) -> tuple[str | None, str | None]:
    from usechange.changelog import git

    default_branch = git.get_default_branch(directory)
    if not default_branch:
        return None, None
    remote_ref = f"origin/{default_branch}"
    if _remote_ref_exists(directory, remote_ref) and _commit_in_remote(
        directory, commit_sha, remote_ref
    ):
        return commit_sha, default_branch
    return default_branch, default_branch


def _tag_exists(directory: str, tag_name: str) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--quiet", "--verify", f"refs/tags/{tag_name}"],
        cwd=directory,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _load_existing_versions(directory: str, output_path: str | None) -> set[str]:
    path = _resolve_changelog_path(directory, output_path)
    if not path:
        return set()
    from usechange.changelog.markdown import parse_changelog

    releases = parse_changelog(path.read_text())
    return {release.version.lstrip("v") for release in releases}


def _resolve_changelog_path(directory: str, output_path: str | None) -> Path | None:
    if output_path is None:
        candidate = Path(directory) / "CHANGELOG.md"
    else:
        candidate = Path(output_path)
        if not candidate.is_absolute():
            candidate = Path(directory) / output_path
    return candidate if candidate.exists() else None


def _resolve_changelog_files(directory: str, changelog_result: object) -> list[str]:
    output_path = getattr(changelog_result, "output_path", None)
    wrote_file = getattr(changelog_result, "wrote_file", False)
    if not wrote_file or not output_path:
        return []
    path = Path(output_path)
    if path.is_absolute():
        return [str(path)]
    return [str(Path(directory) / output_path)]


def _next_available_version(
    directory: str, version: str, existing_versions: set[str]
) -> str:
    from usechange.changelog.semver import bump_version

    candidate = version
    while True:
        if candidate.lstrip("v") not in existing_versions and not _tag_exists(
            directory, f"v{candidate}"
        ):
            return candidate
        bumped = bump_version(candidate, "patch", None)
        if bumped == candidate:
            raise RuntimeError("Unable to auto-bump release version")
        candidate = bumped


def _ensure_src_on_path() -> None:
    root = Path(__file__).resolve().parents[3]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
