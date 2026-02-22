from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ChangeSection:
    title: str
    items: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ReleaseNotes:
    version: str
    date: str | None
    sections: list[ChangeSection] = field(default_factory=list)
    compare_url: str | None = None
    contributors: list[str] = field(default_factory=list)


def render_release(notes: ReleaseNotes) -> str:
    header = f"## {notes.version}"
    if notes.date:
        header = f"{header} ({notes.date})"
    blocks: list[str] = [header, ""]

    for section in notes.sections:
        if not section.items:
            continue
        blocks.append(f"### {section.title}")
        blocks.append("")
        for item in section.items:
            blocks.append(f"- {item}")
        blocks.append("")

    if notes.contributors:
        blocks.append("### Contributors")
        blocks.append("")
        for contributor in notes.contributors:
            blocks.append(f"- {contributor}")
        blocks.append("")

    if notes.compare_url:
        blocks.append(f"[Compare changes]({notes.compare_url})")
        blocks.append("")

    return "\n".join(blocks).rstrip()


def render_changelog(entries: list[ReleaseNotes]) -> str:
    sections: list[str] = ["# Changelog", ""]
    for entry in entries:
        sections.append(render_release(entry))
        sections.append("")
    return "\n".join(sections).rstrip() + "\n"


_RELEASE_HEADER_RE = re.compile(
    r"^##\s+(?P<version>[^\s]+)(?:\s+\((?P<date>[^)]+)\))?$"
)
_SECTION_HEADER_RE = re.compile(r"^###\s+(?P<title>.+)$")


def parse_changelog(content: str) -> list[ReleaseNotes]:
    releases: list[ReleaseNotes] = []
    current_release: ReleaseNotes | None = None
    current_section: ChangeSection | None = None
    contributors: list[str] = []
    compare_url: str | None = None

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        release_match = _RELEASE_HEADER_RE.match(line)
        if release_match:
            if current_release:
                releases.append(
                    ReleaseNotes(
                        version=current_release.version,
                        date=current_release.date,
                        sections=current_release.sections,
                        compare_url=compare_url,
                        contributors=contributors,
                    )
                )
            current_release = ReleaseNotes(
                version=release_match.group("version"),
                date=release_match.group("date"),
                sections=[],
                compare_url=None,
                contributors=[],
            )
            current_section = None
            contributors = []
            compare_url = None
            continue

        if not current_release:
            continue

        section_match = _SECTION_HEADER_RE.match(line)
        if section_match:
            title = section_match.group("title")
            if title.lower() == "contributors":
                current_section = ChangeSection(title=title, items=[])
                continue
            current_section = ChangeSection(title=title, items=[])
            current_release.sections.append(current_section)
            continue

        if line.startswith("[Compare changes]"):
            start = line.find("(")
            end = line.rfind(")")
            if start != -1 and end != -1 and end > start:
                compare_url = line[start + 1 : end]
            continue

        if current_section and line.startswith("-"):
            item = line[1:].strip()
            if current_section.title.lower() == "contributors":
                contributors.append(item)
            else:
                current_section.items.append(item)

    if current_release:
        releases.append(
            ReleaseNotes(
                version=current_release.version,
                date=current_release.date,
                sections=current_release.sections,
                compare_url=compare_url,
                contributors=contributors,
            )
        )

    return releases
