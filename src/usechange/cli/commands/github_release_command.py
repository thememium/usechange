"""GithubReleaseCommand - CLI command."""

from __future__ import annotations

import sys
from pathlib import Path

from usecli import Argument, BaseCommand, Option, console


class GithubReleaseCommand(BaseCommand):
    def signature(self) -> str:
        return "github release"

    def description(self) -> str:
        return "Sync GitHub releases from CHANGELOG.md"

    def handle(
        self,
        versions: list[str] | None = Argument(None, help="Versions or 'all' to sync"),
        directory: str | None = Option(None, "--dir", help="Path to a git repository"),
        token: str | None = Option(None, "--token", help="GitHub token override"),
    ) -> None:
        _ensure_src_on_path()
        from usechange.changelog.cli.gh_release import (
            GhReleaseOptions,
            run_github_release,
        )

        options = GhReleaseOptions(
            versions=versions,
            directory=directory,
            token=token,
        )
        result = run_github_release(options)
        console.print(result.message)


def _ensure_src_on_path() -> None:
    root = Path(__file__).resolve().parents[3]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
