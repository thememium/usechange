from __future__ import annotations

import re
from typing import Protocol, Sequence

from .config import SemverBump, TypeConfig

_VERSION_RE = re.compile(
    r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
    r"(?:-(?P<pre>[^+]+))?(?:\+(?P<meta>.+))?$"
)


def _parse_version(version: str) -> tuple[int, int, int, str | None]:
    match = _VERSION_RE.match(version)
    if not match:
        raise ValueError("invalid version")
    return (
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch")),
        match.group("pre"),
    )


def _next_base_for_bump(
    major: int, minor: int, patch: int, bump: SemverBump
) -> tuple[int, int, int]:
    if major == 0:
        if minor == 0:
            patch += 1
            return major, minor, patch
        if bump in {"major", "premajor"}:
            minor += 1
            patch = 0
            return major, minor, patch
        patch += 1
        return major, minor, patch

    if bump in {"major", "premajor"}:
        return major + 1, 0, 0
    if bump in {"minor", "preminor"}:
        return major, minor + 1, 0
    return major, minor, patch + 1


def _bump_prerelease(pre: str | None, prerelease_id: str | None) -> str:
    label = prerelease_id or "rc"
    if not pre:
        return f"{label}.0"
    if "." in pre:
        base, tail = pre.rsplit(".", 1)
        if base == label and tail.isdigit():
            return f"{label}.{int(tail) + 1}"
    return f"{label}.0"


def bump_version(version: str, bump: SemverBump, prerelease_id: str | None) -> str:
    try:
        major, minor, patch, pre = _parse_version(version)
    except ValueError:
        return version

    if bump == "prerelease":
        if pre:
            pre_value = _bump_prerelease(pre, prerelease_id)
            return f"{major}.{minor}.{patch}-{pre_value}"
        major, minor, patch = _next_base_for_bump(major, minor, patch, "patch")
        return f"{major}.{minor}.{patch}-{_bump_prerelease(None, prerelease_id)}"

    major, minor, patch = _next_base_for_bump(major, minor, patch, bump)
    next_version = f"{major}.{minor}.{patch}"
    if bump.startswith("pre"):
        next_version = f"{next_version}-{_bump_prerelease(None, prerelease_id)}"
    return next_version


class BumpCommit(Protocol):
    @property
    def type(self) -> str: ...

    @property
    def breaking(self) -> bool: ...


_BUMP_ORDER: list[SemverBump] = [
    "patch",
    "minor",
    "major",
    "prepatch",
    "preminor",
    "premajor",
    "prerelease",
]


def determine_bump(
    commits: Sequence[BumpCommit],
    types: dict[str, TypeConfig],
) -> SemverBump | None:
    highest: SemverBump | None = None
    for commit in commits:
        if commit.breaking:
            candidate: SemverBump = "major"
        else:
            config = types.get(commit.type)
            if not config or not config.semver:
                continue
            candidate = config.semver

        if highest is None:
            highest = candidate
        else:
            if _BUMP_ORDER.index(candidate) > _BUMP_ORDER.index(highest):
                highest = candidate
    return highest
