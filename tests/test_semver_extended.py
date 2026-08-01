"""Extended tests for usechange.changelog.semver — version bumping edge cases."""

from __future__ import annotations

from dataclasses import dataclass

from usechange.changelog.config import TypeConfig
from usechange.changelog.semver import (
    _bump_prerelease,
    _next_base_for_bump,
    _parse_version,
    bump_version,
    determine_bump,
)


@dataclass(frozen=True)
class Commit:
    type: str
    breaking: bool


# --- _parse_version ---

def test_parse_version_basic() -> None:
    major, minor, patch, pre = _parse_version("1.2.3")
    assert (major, minor, patch, pre) == (1, 2, 3, None)


def test_parse_version_prerelease() -> None:
    major, minor, patch, pre = _parse_version("1.2.3-alpha.1")
    assert (major, minor, patch, pre) == (1, 2, 3, "alpha.1")


def test_parse_version_metadata() -> None:
    major, minor, patch, pre = _parse_version("1.2.3+build.123")
    assert (major, minor, patch) == (1, 2, 3)
    assert pre is None


def test_parse_version_prerelease_and_metadata() -> None:
    major, minor, patch, pre = _parse_version("1.2.3-beta.1+build")
    assert pre == "beta.1"


def test_parse_version_invalid() -> None:
    try:
        _parse_version("not-a-version")
        assert False, "Should have raised"
    except ValueError:
        pass


# --- bump_version edge cases ---

def test_bump_version_invalid_returns_original() -> None:
    assert bump_version("invalid", "major", None) == "invalid"


def test_bump_version_zero_zero_major() -> None:
    # major=0, minor=0 → bump major → still 0.0.x (patch bump)
    assert bump_version("0.0.1", "major", None) == "0.0.2"


def test_bump_version_zero_zero_minor() -> None:
    assert bump_version("0.0.1", "minor", None) == "0.0.2"


def test_bump_version_zero_zero_patch() -> None:
    assert bump_version("0.0.1", "patch", None) == "0.0.2"


def test_bump_version_zero_major_patch() -> None:
    assert bump_version("0.1.0", "patch", None) == "0.1.1"


def test_bump_version_major_from_zero() -> None:
    assert bump_version("0.5.0", "major", None) == "0.6.0"


def test_bump_version_prerelease_from_scratch() -> None:
    # No existing prerelease → bump patch base and add prerelease
    result = bump_version("1.2.3", "prerelease", None)
    assert result == "1.2.4-rc.0"


def test_bump_version_prerelease_existing_different_label() -> None:
    # Existing prerelease with different label → reset
    result = bump_version("1.2.3-alpha.1", "prerelease", "beta")
    assert result == "1.2.3-beta.0"


def test_bump_version_prerelease_no_dot() -> None:
    # Existing prerelease without dot → reset
    result = bump_version("1.2.3-alpha", "prerelease", "alpha")
    assert result == "1.2.3-alpha.0"


def test_bump_version_premajor_no_prerelease_id() -> None:
    result = bump_version("1.2.3", "premajor", None)
    assert result == "2.0.0-rc.0"


def test_bump_version_preminor_no_prerelease_id() -> None:
    result = bump_version("1.2.3", "preminor", None)
    assert result == "1.3.0-rc.0"


def test_bump_version_prepatch_no_prerelease_id() -> None:
    result = bump_version("1.2.3", "prepatch", None)
    assert result == "1.2.4-rc.0"


# --- _next_base_for_bump edge cases ---

def test_next_base_for_bump_zero_zero() -> None:
    assert _next_base_for_bump(0, 0, 0, "patch") == (0, 0, 1)


def test_next_base_for_bump_zero_zero_major() -> None:
    assert _next_base_for_bump(0, 0, 0, "major") == (0, 0, 1)


def test_next_base_for_bump_zero_minor_major() -> None:
    assert _next_base_for_bump(0, 1, 0, "major") == (0, 2, 0)


def test_next_base_for_bump_zero_minor_patch() -> None:
    assert _next_base_for_bump(0, 1, 0, "patch") == (0, 1, 1)


def test_next_base_for_bump_one_major() -> None:
    assert _next_base_for_bump(1, 0, 0, "major") == (2, 0, 0)


def test_next_base_for_bump_one_minor() -> None:
    assert _next_base_for_bump(1, 0, 0, "minor") == (1, 1, 0)


def test_next_base_for_bump_one_patch() -> None:
    assert _next_base_for_bump(1, 0, 0, "patch") == (1, 0, 1)


# --- _bump_prerelease edge cases ---

def test_bump_prerelease_no_existing() -> None:
    assert _bump_prerelease(None, None) == "rc.0"


def test_bump_prerelease_custom_label() -> None:
    assert _bump_prerelease(None, "beta") == "beta.0"


def test_bump_prerelease_increment() -> None:
    assert _bump_prerelease("rc.3", None) == "rc.4"


def test_bump_prerelease_label_mismatch() -> None:
    # Current is alpha.1 but label is beta → reset
    assert _bump_prerelease("alpha.1", "beta") == "beta.0"


def test_bump_prerelease_no_dot() -> None:
    assert _bump_prerelease("alpha", None) == "rc.0"


def test_bump_prerelease_non_digit_tail() -> None:
    assert _bump_prerelease("rc.abc", None) == "rc.0"


# --- determine_bump edge cases ---

def test_determine_bump_empty_commits() -> None:
    types = {"feat": TypeConfig(title="F", semver="minor")}
    assert determine_bump([], types) is None


def test_determine_bump_no_matching_types() -> None:
    types = {"feat": TypeConfig(title="F", semver="minor")}
    commits = [Commit(type="chore", breaking=False)]
    assert determine_bump(commits, types) is None


def test_determine_bump_breaking_overrides() -> None:
    types = {"fix": TypeConfig(title="F", semver="patch")}
    commits = [Commit(type="fix", breaking=True)]
    assert determine_bump(commits, types) == "major"


def test_determine_bump_major_beats_minor() -> None:
    types = {
        "feat": TypeConfig(title="F", semver="minor"),
        "fix": TypeConfig(title="F", semver="patch"),
    }
    commits = [
        Commit(type="feat", breaking=False),
        Commit(type="fix", breaking=True),
    ]
    assert determine_bump(commits, types) == "major"


def test_determine_bump_only_chore_no_semver() -> None:
    types = {"chore": TypeConfig(title="C", semver=None)}
    commits = [Commit(type="chore", breaking=False)]
    assert determine_bump(commits, types) is None
