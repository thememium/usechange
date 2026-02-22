from __future__ import annotations

from usechange.changelog import git
from usechange.changelog.cli.default import _parse_commit


def test_parse_commit_breaking_footer() -> None:
    commit = git.GitCommit(
        sha="abc123",
        subject="feat(core): add thing",
        body="BREAKING CHANGE: api changed",
        author_name="Dev",
        author_email="dev@example.com",
    )
    parsed = _parse_commit(commit)
    assert parsed is not None
    assert parsed.breaking is True
    assert parsed.type == "feat"


def test_parse_commit_non_conventional() -> None:
    commit = git.GitCommit(
        sha="abc123",
        subject="Update readme",
        body="",
        author_name="Dev",
        author_email="dev@example.com",
    )
    parsed = _parse_commit(commit)
    assert parsed is not None
    assert parsed.type == "other"
