"""Extended tests for usechange.changelog.markdown — parsing edge cases."""

from __future__ import annotations

from usechange.changelog.markdown import (
    ChangeSection,
    ReleaseNotes,
    parse_changelog,
    render_changelog,
    render_release,
)


def test_render_release_with_compare_url() -> None:
    notes = ReleaseNotes(
        version="v1.0.0",
        date=None,
        sections=[ChangeSection(title="Features", items=["A"])],
        compare_url="https://example.com/compare",
    )
    content = render_release(notes)
    assert "[Compare changes](https://example.com/compare)" in content


def test_render_release_with_contributors() -> None:
    notes = ReleaseNotes(
        version="v1.0.0",
        date=None,
        sections=[ChangeSection(title="Features", items=["A"])],
        contributors=["Alice <a@b.com>"],
    )
    content = render_release(notes)
    assert "### Contributors" in content
    assert "- Alice <a@b.com>" in content


def test_render_release_empty_sections() -> None:
    notes = ReleaseNotes(
        version="v1.0.0",
        date=None,
        sections=[ChangeSection(title="Empty", items=[])],
    )
    content = render_release(notes)
    assert "Empty" not in content  # Empty sections are skipped


def test_render_changelog_multiple() -> None:
    entries = [
        ReleaseNotes(version="v2.0.0", date=None, sections=[ChangeSection(title="F", items=["A"])]),
        ReleaseNotes(version="v1.0.0", date=None, sections=[ChangeSection(title="F", items=["B"])]),
    ]
    content = render_changelog(entries)
    assert "# Changelog" in content
    assert "v2.0.0" in content
    assert "v1.0.0" in content
    assert content.endswith("\n")


def test_parse_changelog_no_releases() -> None:
    assert parse_changelog("# Changelog\n\n") == []


def test_parse_changelog_with_compare_url() -> None:
    content = (
        "# Changelog\n\n"
        "## v1.0.0\n\n"
        "[Compare changes](https://example.com/compare)\n\n"
        "### Features\n\n- A\n\n"
    )
    releases = parse_changelog(content)
    assert len(releases) == 1
    assert releases[0].compare_url == "https://example.com/compare"


def test_parse_changelog_with_contributors() -> None:
    content = (
        "# Changelog\n\n"
        "## v1.0.0\n\n"
        "### Features\n\n- A\n\n"
        "### Contributors\n\n- Alice <a@b.com>\n\n"
    )
    releases = parse_changelog(content)
    assert len(releases) == 1
    assert "Alice <a@b.com>" in releases[0].contributors


def test_parse_changelog_multiple_releases() -> None:
    content = (
        "# Changelog\n\n"
        "## v2.0.0\n\n### F\n\n- B\n\n"
        "## v1.0.0\n\n### F\n\n- A\n\n"
    )
    releases = parse_changelog(content)
    assert len(releases) == 2
    assert releases[0].version == "v2.0.0"
    assert releases[1].version == "v1.0.0"


def test_parse_changelog_date_in_header() -> None:
    content = "# Changelog\n\n## v1.0.0 (2024-01-15)\n\n### F\n\n- A\n\n"
    releases = parse_changelog(content)
    assert releases[0].date == "2024-01-15"


def test_parse_changelog_skips_content_before_first_release() -> None:
    content = "# Changelog\n\nSome preamble text\n\n## v1.0.0\n\n### F\n\n- A\n\n"
    releases = parse_changelog(content)
    assert len(releases) == 1
