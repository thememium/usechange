"""ChangelogCommand - CLI command."""

from __future__ import annotations

import sys
from pathlib import Path

from usecli import Argument, BaseCommand, Option, console

from usechange.cli.commands import print_error


class ChangelogCommand(BaseCommand):
    def signature(self) -> str:
        return "changelog"

    def description(self) -> str:
        return "Generate changelog entries from Conventional Commits"

    def aliases(self) -> list[str]:
        return ["log"]

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
            False,
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
        from usechange.changelog.cli.default import ChangelogOptions, run_changelog

        effective_no_output = no_output or (output is None and not write_output)
        options = ChangelogOptions(
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
        )
        result = run_changelog(options)
        if (
            not result.content
            and result.output_path is None
            and result.new_version is None
        ):
            print_error(result.message)
            return
        if result.output_path:
            console.print(result.message)
        elif result.content:
            console.print(result.content)
        else:
            console.print(result.message)


def _ensure_src_on_path() -> None:
    root = Path(__file__).resolve().parents[3]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
