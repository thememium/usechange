from __future__ import annotations

from dataclasses import dataclass

from usechange.changelog.config import TypeConfig
from usechange.changelog.semver import bump_version, determine_bump


@dataclass(frozen=True)
class Commit:
    type: str
    breaking: bool


def test_bump_version_major() -> None:
    assert bump_version("1.2.3", "major", None) == "2.0.0"


def test_bump_version_zero_major_maps_to_minor() -> None:
    assert bump_version("0.1.5", "major", None) == "0.2.0"


def test_bump_version_prerelease_minor() -> None:
    assert bump_version("1.2.3", "preminor", "alpha") == "1.3.0-alpha.0"


def test_bump_version_prerelease_increment() -> None:
    assert bump_version("1.2.3-alpha.1", "prerelease", "alpha") == "1.2.3-alpha.2"


def test_determine_bump_from_commits() -> None:
    types = {
        "feat": TypeConfig(title="Enhancements", semver="minor"),
        "fix": TypeConfig(title="Fixes", semver="patch"),
    }
    commits = [Commit(type="fix", breaking=False), Commit(type="feat", breaking=False)]
    assert determine_bump(commits, types) == "minor"
