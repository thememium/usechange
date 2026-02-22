from __future__ import annotations

import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from usechange.changelog import git
from usechange.changelog.github import GitHubReleaseRequest, sync_release
from usechange.changelog.markdown import ReleaseNotes, parse_changelog, render_release
from usechange.changelog.repo import resolve_repo


@dataclass(frozen=True)
class GhReleaseOptions:
    versions: list[str] | None
    directory: str | None
    token: str | None


@dataclass(frozen=True)
class GhReleaseResult:
    message: str


def run_github_release(options: GhReleaseOptions) -> GhReleaseResult:
    directory = str(Path(options.directory or ".").resolve())
    changelog = _load_changelog(directory)
    releases = parse_changelog(changelog)

    if not releases:
        return GhReleaseResult(message="No releases found in changelog.")

    requested = _resolve_versions(options.versions, releases)
    repo_info = resolve_repo(None, directory)
    repo_slug = repo_info.repo if repo_info else None

    synced = []
    for release in requested:
        body = render_release(release)
        request = GitHubReleaseRequest(
            version=release.version.lstrip("v"),
            body=body,
            token=options.token,
            repo=repo_slug,
        )
        sync_release(request)
        synced.append(release.version)

    message = "Synced GitHub releases: " + ", ".join(synced)
    return GhReleaseResult(message=message)


def _resolve_versions(
    versions: list[str] | None,
    releases: list[ReleaseNotes],
) -> list[ReleaseNotes]:
    if not versions:
        return [releases[0]]
    if len(versions) == 1 and versions[0] == "all":
        return releases
    selected = []
    target_set = {version.lstrip("v") for version in versions}
    for release in releases:
        if release.version.lstrip("v") in target_set:
            selected.append(release)
    if not selected:
        raise RuntimeError("No matching releases found in changelog")
    return selected


def _load_changelog(directory: str) -> str:
    path = Path(directory) / "CHANGELOG.md"
    if path.exists():
        return path.read_text()
    repo_info = resolve_repo(None, directory)
    if not repo_info or not repo_info.repo:
        raise RuntimeError("Missing changelog and repository metadata")
    branch = git.get_default_branch(directory) or "main"
    url = f"https://raw.githubusercontent.com/{repo_info.repo}/{branch}/CHANGELOG.md"
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        raise RuntimeError("Unable to fetch changelog from GitHub") from error
