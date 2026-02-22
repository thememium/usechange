from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass

from .config import RepoConfig


@dataclass(frozen=True)
class RepoInfo:
    domain: str | None
    repo: str | None
    provider: str | None


def _run_git(directory: str, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=directory,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def _normalize_remote_url(url: str) -> str | None:
    url = url.strip()
    if not url:
        return None
    url = url.removesuffix(".git")
    if url.startswith("git@"):
        parts = url.split(":", 1)
        if len(parts) == 2:
            host = parts[0].split("@")[-1]
            return f"https://{host}/{parts[1]}"
    if url.startswith("http://"):
        url = "https://" + url[len("http://") :]
    return url


def _parse_repo(url: str) -> RepoInfo | None:
    normalized = _normalize_remote_url(url)
    if not normalized:
        return None
    match = re.match(r"https://([^/]+)/([^/]+/[^/]+)$", normalized)
    if not match:
        return RepoInfo(domain=None, repo=normalized, provider=None)
    domain = match.group(1)
    repo = match.group(2)
    provider = None
    if "github" in domain:
        provider = "github"
    elif "gitlab" in domain:
        provider = "gitlab"
    elif "bitbucket" in domain:
        provider = "bitbucket"
    return RepoInfo(domain=domain, repo=repo, provider=provider)


def resolve_repo(
    repo: str | RepoInfo | RepoConfig | None, directory: str | None = None
) -> RepoInfo | None:
    if isinstance(repo, RepoInfo):
        return repo
    if isinstance(repo, RepoConfig):
        return RepoInfo(domain=repo.domain, repo=repo.repo, provider=repo.provider)
    if isinstance(repo, str) and repo:
        return _parse_repo(repo)
    if directory:
        try:
            url = _run_git(directory, ["remote", "get-url", "origin"])
        except RuntimeError:
            return None
        return _parse_repo(url)
    return None


def commit_url(info: RepoInfo | None, sha: str) -> str | None:
    if not info or not info.domain or not info.repo:
        return None
    return f"https://{info.domain}/{info.repo}/commit/{sha}"


def compare_url(info: RepoInfo | None, from_ref: str, to_ref: str) -> str | None:
    if not info or not info.domain or not info.repo:
        return None
    return f"https://{info.domain}/{info.repo}/compare/{from_ref}...{to_ref}"
