from __future__ import annotations

from usechange.changelog.cli import default as changelog_default
from usechange.changelog.config import TypeConfig, default_types


def test_strip_emoji_from_types_defaults() -> None:
    types = default_types()
    stripped = changelog_default._strip_emoji_from_types(types)

    assert stripped["feat"].title == "Enhancements"
    assert stripped["fix"].title == "Fixes"


def test_strip_emoji_from_types_no_emoji() -> None:
    types = {"custom": TypeConfig(title="Custom Title")}
    stripped = changelog_default._strip_emoji_from_types(types)

    assert stripped["custom"].title == "Custom Title"
