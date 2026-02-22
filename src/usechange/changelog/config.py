from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import tomli as tomllib

SemverBump = Literal[
    "major",
    "minor",
    "patch",
    "premajor",
    "preminor",
    "prepatch",
    "prerelease",
]


@dataclass(frozen=True)
class TypeConfig:
    title: str
    semver: SemverBump | None = None


@dataclass(frozen=True)
class PublishConfig:
    args: list[str] = field(default_factory=list)
    tag: str = "latest"
    private: bool = False


@dataclass(frozen=True)
class TemplatesConfig:
    commit_message: str = "chore(release): v{{newVersion}}"
    tag_message: str = "v{{newVersion}}"
    tag_body: str = "v{{newVersion}}"


@dataclass(frozen=True)
class RepoConfig:
    domain: str | None = None
    repo: str | None = None
    provider: str | None = None


@dataclass(frozen=True)
class ChangelogConfig:
    cwd: str = "."
    types: dict[str, TypeConfig] = field(default_factory=dict)
    scope_map: dict[str, str] = field(default_factory=dict)
    repo: RepoConfig | str | None = None
    tokens: dict[str, str] = field(default_factory=dict)
    from_ref: str = ""
    to_ref: str = ""
    new_version: str | None = None
    sign_tags: bool | None = None
    output: str | bool = "CHANGELOG.md"
    publish: PublishConfig = field(default_factory=PublishConfig)
    templates: TemplatesConfig = field(default_factory=TemplatesConfig)
    no_authors: bool = False
    exclude_authors: list[str] = field(default_factory=list)
    hide_author_email: bool | None = None


def default_types() -> dict[str, TypeConfig]:
    return {
        "feat": TypeConfig(title="🚀 Enhancements", semver="minor"),
        "perf": TypeConfig(title="🔥 Performance", semver="patch"),
        "fix": TypeConfig(title="🩹 Fixes", semver="patch"),
        "refactor": TypeConfig(title="💅 Refactors", semver="patch"),
        "docs": TypeConfig(title="📖 Documentation", semver="patch"),
        "build": TypeConfig(title="📦 Build", semver="patch"),
        "types": TypeConfig(title="🌊 Types", semver="patch"),
        "chore": TypeConfig(title="🏡 Chore"),
        "examples": TypeConfig(title="🏀 Examples"),
        "test": TypeConfig(title="✅ Tests"),
        "style": TypeConfig(title="🎨 Styles"),
        "ci": TypeConfig(title="🤖 CI"),
    }


def get_default_config() -> ChangelogConfig:
    return ChangelogConfig(
        types=default_types(),
        tokens={},
        publish=PublishConfig(),
        templates=TemplatesConfig(),
    )


def resolve_config(overrides: dict[str, object] | None = None) -> ChangelogConfig:
    config = get_default_config()
    if not overrides:
        return config

    payload = config.__dict__.copy()
    for key, value in overrides.items():
        if key not in payload or value is None:
            continue
        payload[key] = value
    return ChangelogConfig(**payload)


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _read_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return tomllib.loads(path.read_text())


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _merge_types(
    defaults: dict[str, TypeConfig], overrides: dict[str, Any] | None
) -> dict[str, TypeConfig]:
    if not overrides:
        return defaults
    merged = defaults.copy()
    for key, value in overrides.items():
        if value is False:
            merged.pop(key, None)
            continue
        if isinstance(value, dict):
            merged[key] = TypeConfig(
                title=str(value.get("title", key)),
                semver=value.get("semver"),
            )
    return merged


def _load_config_payload(cwd: Path) -> dict[str, Any]:
    config_files = [
        cwd / "changelog.config.json",
        cwd / ".changelogrc",
        cwd / "changelog.config.toml",
    ]
    for path in config_files:
        if path.name.endswith(".toml"):
            data = _read_toml(path)
        else:
            data = _read_json(path)
        if data:
            return data

    pyproject = _read_toml(cwd / "pyproject.toml")
    tool_section = pyproject.get("tool", {})
    return tool_section.get("changelog", {}) if isinstance(tool_section, dict) else {}


def load_config(cwd: str) -> ChangelogConfig:
    base = Path(cwd)
    _load_dotenv(base / ".env")
    payload = _load_config_payload(base)
    defaults = get_default_config()

    types_payload = payload.get("types") if isinstance(payload, dict) else None
    merged_types = _merge_types(defaults.types, types_payload)

    tokens = payload.get("tokens", {}) if isinstance(payload, dict) else {}
    github_token = (
        os.environ.get("CHANGELOGEN_TOKENS_GITHUB")
        or os.environ.get("GITHUB_TOKEN")
        or os.environ.get("GH_TOKEN")
    )
    if github_token and "github" not in tokens:
        tokens = {**tokens, "github": github_token}

    publish_payload = payload.get("publish", {}) if isinstance(payload, dict) else {}
    templates_payload = (
        payload.get("templates", {}) if isinstance(payload, dict) else {}
    )
    repo_payload = payload.get("repo") if isinstance(payload, dict) else None

    return resolve_config(
        {
            "cwd": str(base),
            "types": merged_types,
            "scope_map": payload.get("scopeMap", {}),
            "repo": repo_payload,
            "tokens": tokens,
            "from_ref": payload.get("from", ""),
            "to_ref": payload.get("to", ""),
            "new_version": payload.get("newVersion"),
            "sign_tags": payload.get("signTags"),
            "output": payload.get("output", defaults.output),
            "publish": PublishConfig(
                args=list(publish_payload.get("args", [])),
                tag=publish_payload.get("tag", defaults.publish.tag),
                private=bool(publish_payload.get("private", False)),
            ),
            "templates": TemplatesConfig(
                commit_message=templates_payload.get(
                    "commitMessage", defaults.templates.commit_message
                ),
                tag_message=templates_payload.get(
                    "tagMessage", defaults.templates.tag_message
                ),
                tag_body=templates_payload.get("tagBody", defaults.templates.tag_body),
            ),
            "exclude_authors": payload.get("excludeAuthors", []),
            "no_authors": bool(payload.get("noAuthors", False)),
            "hide_author_email": payload.get("hideAuthorEmail"),
        }
    )
