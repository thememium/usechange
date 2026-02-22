from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from usecli import BaseCommand, Confirm, Option, console


class ReleaseCommand(BaseCommand):
    def signature(self) -> str:
        return "release"

    def description(self) -> str:
        return "Run release workflow using usechange changelog"

    def handle(
        self,
        directory: str | None = Option(None, "--dir", help="Path to a git repository"),
        yes: bool = Option(False, "--yes", "-y", help="Skip confirmation"),
    ) -> None:
        _ensure_src_on_path()
        from usechange.changelog.cli.default import ChangelogOptions, run_changelog

        if not yes and not Confirm.ask("Continue with release?"):
            console.print("Release cancelled.")
            return

        resolved_dir = str(Path(directory or ".").resolve())
        changelog_result = run_changelog(
            ChangelogOptions(
                repo_dir=None,
                from_ref=None,
                to_ref=None,
                directory=resolved_dir,
                clean=False,
                output="CHANGELOG.md",
                no_output=False,
                no_authors=False,
                hide_author_email=False,
                bump=True,
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
            )
        )

        version = changelog_result.new_version
        if not version:
            raise RuntimeError("Unable to determine release version")

        _run(resolved_dir, ["uv", "version", version])
        _run(resolved_dir, ["uv", "sync"])
        _run(resolved_dir, ["uv", "lock"])

        _run(
            resolved_dir,
            [
                "git",
                "add",
                "CHANGELOG.md",
                "pyproject.toml",
                "uv.lock",
            ],
        )
        _run(resolved_dir, ["git", "commit", "-m", "chore(uv): update version"])
        tag_name = f"v{version}"
        _run(resolved_dir, ["git", "tag", tag_name])
        _run(resolved_dir, ["git", "push"])
        _run(resolved_dir, ["git", "push", "origin", tag_name])

        notes = _extract_release_notes(resolved_dir, tag_name)
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as handle:
            handle.write(notes)
            notes_file = handle.name

        target_sha = _run_capture(resolved_dir, ["git", "rev-parse", tag_name])
        if _gh_release_exists(resolved_dir, tag_name):
            _run(
                resolved_dir,
                ["gh", "release", "edit", tag_name, "--notes-file", notes_file],
            )
        else:
            _run(
                resolved_dir,
                [
                    "gh",
                    "release",
                    "create",
                    tag_name,
                    "--target",
                    target_sha,
                    "--notes-file",
                    notes_file,
                ],
            )
        console.print(f"Release {version} completed.")


def _run(directory: str, args: list[str]) -> None:
    result = subprocess.run(args, cwd=directory, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(args)}")


def _run_capture(directory: str, args: list[str]) -> str:
    result = subprocess.run(
        args,
        cwd=directory,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(args)}")
    return result.stdout.strip()


def _extract_release_notes(directory: str, tag_name: str) -> str:
    changelog = Path(directory) / "CHANGELOG.md"
    lines = changelog.read_text().splitlines()
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


def _ensure_src_on_path() -> None:
    root = Path(__file__).resolve().parents[3]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
