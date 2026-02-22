from __future__ import annotations

from usechange.changelog.markdown import (
    ChangeSection,
    ReleaseNotes,
    parse_changelog,
    render_changelog,
)


def test_render_and_parse_changelog_roundtrip() -> None:
    notes = ReleaseNotes(
        version="v1.2.3",
        date="2026-02-22",
        sections=[
            ChangeSection(title="Enhancements", items=["Add feature A"]),
            ChangeSection(title="Fixes", items=["Fix bug B"]),
        ],
        compare_url="https://example.com/compare/v1.2.2...v1.2.3",
        contributors=["Alice <alice@example.com>"],
    )
    content = render_changelog([notes])
    parsed = parse_changelog(content)

    assert len(parsed) == 1
    assert parsed[0].version == "v1.2.3"
    assert parsed[0].date == "2026-02-22"
    assert parsed[0].compare_url == "https://example.com/compare/v1.2.2...v1.2.3"
    assert parsed[0].contributors == ["Alice <alice@example.com>"]
    assert parsed[0].sections[0].title == "Enhancements"
    assert parsed[0].sections[0].items == ["Add feature A"]
