from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GitCommit:
    sha: str
    subject: str
    body: str
    author_name: str
    author_email: str


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


def get_repo_root(directory: str) -> str | None:
    try:
        output = _run_git(directory, ["rev-parse", "--show-toplevel"])
    except RuntimeError:
        return None
    return str(Path(output))


def is_clean(directory: str) -> bool:
    output = _run_git(directory, ["status", "--porcelain"])
    return output == ""


def get_latest_tag(directory: str) -> str | None:
    try:
        output = _run_git(directory, ["describe", "--tags", "--abbrev=0"])
    except RuntimeError:
        return None
    return output or None


def get_current_ref(directory: str) -> str:
    return _run_git(directory, ["rev-parse", "HEAD"])


def get_short_ref(directory: str) -> str:
    return _run_git(directory, ["rev-parse", "--short", "HEAD"])


def get_log(
    directory: str, from_ref: str | None, to_ref: str | None
) -> list[GitCommit]:
    range_part = None
    if from_ref and to_ref:
        range_part = f"{from_ref}..{to_ref}"
    elif from_ref:
        range_part = f"{from_ref}..HEAD"
    elif to_ref:
        range_part = to_ref

    format_str = "%H%x1f%an%x1f%ae%x1f%s%x1f%b%x1e"
    args = ["log", f"--format={format_str}"]
    if range_part:
        args.append(range_part)
    output = _run_git(directory, args)
    commits: list[GitCommit] = []
    for entry in output.split("\x1e"):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split("\x1f")
        if len(parts) < 5:
            continue
        sha, author_name, author_email, subject, body = parts[:5]
        commits.append(
            GitCommit(
                sha=sha,
                subject=subject.strip(),
                body=body.strip(),
                author_name=author_name.strip(),
                author_email=author_email.strip(),
            )
        )
    return commits


def get_default_branch(directory: str) -> str | None:
    try:
        ref = _run_git(directory, ["symbolic-ref", "refs/remotes/origin/HEAD"])
    except RuntimeError:
        return None
    if ref.startswith("refs/remotes/origin/"):
        return ref.split("refs/remotes/origin/")[-1]
    return None
