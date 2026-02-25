from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path

from usechange.changelog import git
from usechange.changelog.config import (
    ChangelogConfig,
    TypeConfig,
    load_config,
    resolve_config,
)
from usechange.changelog.markdown import (
    ChangeSection,
    ReleaseNotes,
    parse_changelog,
    render_changelog,
)
from usechange.changelog.repo import RepoInfo, commit_url, compare_url, resolve_repo
from usechange.changelog.semver import SemverBump, bump_version, determine_bump


@dataclass(frozen=True)
class ChangelogOptions:
    repo_dir: str | None
    from_ref: str | None
    to_ref: str | None
    directory: str | None
    clean: bool
    output: str | None
    no_output: bool
    no_authors: bool
    include_emojis: bool
    include_date: bool
    hide_author_email: bool
    bump: bool
    release_version: str | None
    release: bool
    no_commit: bool
    no_tag: bool
    push: bool
    no_github: bool
    publish: bool
    publish_tag: str
    name_suffix: str | None
    version_suffix: str | None
    canary: str | None
    major: bool
    minor: bool
    patch: bool
    premajor: str | None
    preminor: str | None
    prepatch: str | None
    prerelease: str | None
    preview_next_version: bool = False
    update_versions: bool = True


@dataclass(frozen=True)
class ChangelogResult:
    message: str
    content: str
    output_path: str | None
    new_version: str | None
    wrote_file: bool
    resolved_dir: str


def run_changelog(options: ChangelogOptions) -> ChangelogResult:
    resolved_dir = options.directory or options.repo_dir or "."
    directory = str(Path(resolved_dir).resolve())

    if options.clean and not git.is_clean(directory):
        return ChangelogResult(
            message="Working directory is not clean.",
            content="",
            output_path=None,
            new_version=None,
            wrote_file=False,
            resolved_dir=directory,
        )

    config = _resolve_config_from_options(directory, options)
    if not options.include_emojis:
        config = replace(config, types=_strip_emoji_from_types(config.types))
    repo_info: RepoInfo | None = resolve_repo(config.repo, directory)
    from_ref = config.from_ref or git.get_latest_tag(directory)
    to_ref = config.to_ref or "HEAD"

    commits = git.get_log(directory, from_ref, to_ref)
    parsed_commits = [_parse_commit(commit) for commit in commits]
    parsed_commits = [commit for commit in parsed_commits if commit is not None]

    sections = _group_commits(parsed_commits, config.types, repo_info)

    contributors = []
    if not config.no_authors and not options.no_authors:
        contributors = _collect_contributors(
            parsed_commits,
            config.exclude_authors,
            options.hide_author_email or bool(config.hide_author_email),
        )

    version = _resolve_version(directory, options, config, parsed_commits)
    output_path = _resolve_output_path(options, config)
    compare_to_ref = _resolve_compare_to_ref(
        options, config, to_ref, version, output_path
    )
    compare_from_ref = from_ref
    if (
        compare_from_ref
        and compare_from_ref == compare_to_ref
        and compare_to_ref != "HEAD"
    ):
        previous_tag = git.get_previous_tag(directory, compare_from_ref)
        if previous_tag:
            compare_from_ref = previous_tag
    compare_link = None
    if compare_from_ref:
        compare_link = compare_url(repo_info, compare_from_ref, compare_to_ref)
    date = None
    if options.include_date:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    notes = ReleaseNotes(
        version=f"v{version}",
        date=date,
        sections=sections,
        compare_url=compare_link,
        contributors=contributors,
    )

    content = _merge_changelog(directory, output_path=output_path, new_notes=notes)
    wrote_file = False
    if output_path:
        target_path = Path(directory) / output_path
        target_path.write_text(content)
        wrote_file = True

    if (
        options.bump or options.release or options.release_version
    ) and options.update_versions:
        _update_versions(directory, version)

    message = f"Changelog generated for {version}."
    return ChangelogResult(
        message=message,
        content=content,
        output_path=output_path,
        new_version=version,
        wrote_file=wrote_file,
        resolved_dir=directory,
    )


_CONVENTIONAL_RE = re.compile(
    r"^(?P<type>[a-zA-Z]+)(\((?P<scope>[^)]+)\))?(?P<bang>!)?: (?P<subject>.+)$"
)
_BREAKING_RE = re.compile(r"^BREAKING[ -]CHANGE:", re.MULTILINE)
_REF_RE = re.compile(r"#(\d+)")


@dataclass(frozen=True)
class ParsedCommit:
    sha: str
    short_sha: str
    type: str
    scope: str | None
    subject: str
    breaking: bool
    author_name: str
    author_email: str
    references: list[str]


def _parse_commit(commit: git.GitCommit) -> ParsedCommit | None:
    match = _CONVENTIONAL_RE.match(commit.subject)
    if not match:
        commit_type = "other"
        subject = commit.subject
        scope = None
        breaking = False
    else:
        commit_type = match.group("type")
        subject = match.group("subject").strip()
        scope = match.group("scope")
        breaking = bool(match.group("bang"))

    if _BREAKING_RE.search(commit.body):
        breaking = True

    references = []
    for ref in _REF_RE.findall(f"{commit.subject}\n{commit.body}"):
        references.append(f"#{ref}")

    return ParsedCommit(
        sha=commit.sha,
        short_sha=commit.sha[:7],
        type=commit_type,
        scope=scope,
        subject=subject,
        breaking=breaking,
        author_name=commit.author_name,
        author_email=commit.author_email,
        references=references,
    )


def _group_commits(
    commits: list[ParsedCommit],
    types: dict[str, TypeConfig],
    repo_info: RepoInfo | None,
) -> list[ChangeSection]:
    grouped: dict[str, list[str]] = {}

    for commit in commits:
        if commit.type in types:
            title = types[commit.type].title
        else:
            title = "Other Changes"

        item = _format_commit(commit, repo_info)
        grouped.setdefault(title, []).append(item)

    ordered_sections: list[ChangeSection] = []
    for type_key, config in types.items():
        if config.title in grouped:
            ordered_sections.append(
                ChangeSection(title=config.title, items=grouped[config.title])
            )
    if "Other Changes" in grouped:
        ordered_sections.append(
            ChangeSection(title="Other Changes", items=grouped["Other Changes"])
        )
    return ordered_sections


def _strip_emoji_from_title(title: str) -> str:
    stripped = re.sub(r"^[^A-Za-z0-9]+\s*", "", title).strip()
    return stripped if stripped else title


def _strip_emoji_from_types(
    types: dict[str, TypeConfig],
) -> dict[str, TypeConfig]:
    return {
        key: replace(config, title=_strip_emoji_from_title(config.title))
        for key, config in types.items()
    }


def _format_commit(commit: ParsedCommit, repo_info: RepoInfo | None) -> str:
    scope = f"**{commit.scope}**: " if commit.scope else ""
    line = f"{scope}{commit.subject}"
    if commit.references:
        refs = ", ".join(commit.references)
        line = f"{line} ({refs})"
    url = commit_url(repo_info, commit.sha)
    if url:
        line = f"{line} ([{commit.short_sha}]({url}))"
    else:
        line = f"{line} ({commit.short_sha})"
    return line


def _collect_contributors(
    commits: list[ParsedCommit],
    exclude: list[str],
    hide_email: bool,
) -> list[str]:
    seen = set()
    contributors: list[str] = []
    for commit in commits:
        if commit.author_name in exclude or commit.author_email in exclude:
            continue
        if hide_email:
            entry = commit.author_name
        else:
            entry = f"{commit.author_name} <{commit.author_email}>"
        if entry in seen:
            continue
        seen.add(entry)
        contributors.append(entry)
    return contributors


def _resolve_version(
    directory: str,
    options: ChangelogOptions,
    config: ChangelogConfig,
    commits: list[ParsedCommit],
) -> str:
    if options.release_version:
        return options.release_version

    current_version = _read_current_version(directory)
    if not current_version:
        current_version = "0.0.0"

    bump = _resolve_bump(options, config, commits)
    if bump is None and options.preview_next_version:
        bump = determine_bump(commits, config.types)
    if not bump:
        return current_version

    prerelease_id = _resolve_prerelease_id(options)
    next_version = bump_version(current_version, bump, prerelease_id)
    suffix = _resolve_version_suffix(directory, options)
    if suffix:
        next_version = f"{next_version}-{suffix}"
    return next_version


def _version_tag(version: str) -> str:
    if version.startswith("v"):
        return version
    return f"v{version}"


def _resolve_bump(
    options: ChangelogOptions,
    config: ChangelogConfig,
    commits: list[ParsedCommit],
) -> SemverBump | None:
    if options.major:
        return "major"
    if options.minor:
        return "minor"
    if options.patch:
        return "patch"
    if options.premajor is not None:
        return "premajor"
    if options.preminor is not None:
        return "preminor"
    if options.prepatch is not None:
        return "prepatch"
    if options.prerelease is not None:
        return "prerelease"

    if not options.bump and not options.release:
        return None

    return determine_bump(commits, config.types)


def _resolve_prerelease_id(options: ChangelogOptions) -> str | None:
    if options.premajor:
        return options.premajor
    if options.preminor:
        return options.preminor
    if options.prepatch:
        return options.prepatch
    if options.prerelease:
        return options.prerelease
    return None


def _resolve_version_suffix(directory: str, options: ChangelogOptions) -> str | None:
    if options.canary is not None:
        if options.canary and options.canary != "true":
            return options.canary
        return _timestamp_suffix(directory)
    if not options.version_suffix:
        return None
    if options.version_suffix == "true":
        return _timestamp_suffix(directory)
    return options.version_suffix


def _timestamp_suffix(directory: str) -> str:
    short_ref = git.get_short_ref(directory)
    return datetime.now(timezone.utc).strftime("%y%m%d-%H%M%S-") + short_ref


def _read_current_version(directory: str) -> str | None:
    pyproject = Path(directory) / "pyproject.toml"
    if not pyproject.exists():
        return None
    content = pyproject.read_text()
    match = re.search(r"^version\s*=\s*\"([^\"]+)\"", content, re.MULTILINE)
    if not match:
        return None
    return match.group(1)


def _resolve_output_path(
    options: ChangelogOptions, config: ChangelogConfig
) -> str | None:
    if options.no_output:
        return None
    if config.output is False:
        return None
    if options.output:
        return options.output
    if config.output is True:
        return "CHANGELOG.md"
    return str(config.output)


def _resolve_compare_to_ref(
    options: ChangelogOptions,
    config: ChangelogConfig,
    to_ref: str,
    version: str,
    output_path: str | None,
) -> str:
    if config.to_ref:
        return config.to_ref
    if output_path is None:
        return to_ref
    return _version_tag(version)


def _merge_changelog(
    directory: str,
    output_path: str | None,
    new_notes: ReleaseNotes,
) -> str:
    existing_notes: list[ReleaseNotes] = []
    if output_path:
        path = Path(directory) / output_path
        if path.exists():
            existing_notes = parse_changelog(path.read_text())

    version_key = new_notes.version.lstrip("v")
    filtered = [
        note for note in existing_notes if note.version.lstrip("v") != version_key
    ]
    return render_changelog([new_notes, *filtered])


def _resolve_config_from_options(
    directory: str, options: ChangelogOptions
) -> ChangelogConfig:
    config = load_config(directory)
    overrides: dict[str, object] = {}
    if options.from_ref:
        overrides["from_ref"] = options.from_ref
    if options.to_ref:
        overrides["to_ref"] = options.to_ref
    if options.no_authors:
        overrides["no_authors"] = True
    if options.hide_author_email:
        overrides["hide_author_email"] = True
    if options.output:
        overrides["output"] = options.output
    return resolve_config({**config.__dict__, **overrides})


def _update_versions(directory: str, version: str) -> None:
    _update_package_json_version(directory, version)
    _update_pyproject_version(directory, version)


def _update_package_json_version(directory: str, version: str) -> None:
    path = Path(directory) / "package.json"
    if not path.exists():
        return
    data = json.loads(path.read_text())
    data["version"] = version
    path.write_text(json.dumps(data, indent=2) + "\n")


def _update_pyproject_version(directory: str, version: str) -> None:
    path = Path(directory) / "pyproject.toml"
    if not path.exists():
        return
    content = path.read_text()
    updated = re.sub(
        r"^version\s*=\s*\"[^\"]+\"",
        f'version = "{version}"',
        content,
        flags=re.MULTILINE,
    )
    path.write_text(updated)
