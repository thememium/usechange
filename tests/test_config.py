"""Tests for usechange.changelog.config — config loading and merging."""

from __future__ import annotations

import json
import os
from pathlib import Path

from usechange.changelog.config import (
    ChangelogConfig,
    _load_config_payload,
    _load_dotenv,
    _merge_types,
    _read_json,
    _read_toml,
    default_types,
    get_default_config,
    load_config,
    resolve_config,
)

# --- default_types / get_default_config ---


def test_default_types_has_feat() -> None:
    types = default_types()
    assert "feat" in types
    assert types["feat"].semver == "minor"


def test_default_types_has_fix() -> None:
    types = default_types()
    assert types["fix"].semver == "patch"


def test_get_default_config_returns_changelog_config() -> None:
    config = get_default_config()
    assert isinstance(config, ChangelogConfig)
    assert config.types == default_types()


# --- resolve_config ---


def test_resolve_config_no_overrides() -> None:
    config = resolve_config()
    assert config.types == default_types()


def test_resolve_config_with_overrides() -> None:
    config = resolve_config({"from_ref": "v1.0.0", "to_ref": "HEAD"})
    assert config.from_ref == "v1.0.0"
    assert config.to_ref == "HEAD"


def test_resolve_config_ignores_none_values() -> None:
    config = resolve_config({"from_ref": None, "to_ref": "HEAD"})
    assert config.from_ref == ""
    assert config.to_ref == "HEAD"


def test_resolve_config_ignores_unknown_keys() -> None:
    config = resolve_config({"unknown_key": "value"})
    assert isinstance(config, ChangelogConfig)


# --- _merge_types ---


def test_merge_types_no_overrides() -> None:
    defaults = default_types()
    assert _merge_types(defaults, None) == defaults


def test_merge_types_empty_overrides() -> None:
    defaults = default_types()
    assert _merge_types(defaults, {}) == defaults


def test_merge_types_add_custom() -> None:
    defaults = default_types()
    merged = _merge_types(defaults, {"custom": {"title": "Custom", "semver": "patch"}})
    assert "custom" in merged
    assert merged["custom"].title == "Custom"
    assert merged["custom"].semver == "patch"


def test_merge_types_disable_type() -> None:
    defaults = default_types()
    merged = _merge_types(defaults, {"feat": False})
    assert "feat" not in merged


def test_merge_types_override_title() -> None:
    defaults = default_types()
    merged = _merge_types(defaults, {"feat": {"title": "New Title"}})
    assert merged["feat"].title == "New Title"


def test_merge_types_override_no_semver() -> None:
    defaults = default_types()
    merged = _merge_types(defaults, {"feat": {"title": "Features"}})
    assert merged["feat"].semver is None


# --- _read_toml / _read_json ---


def test_read_toml_existing(tmp_path: Path) -> None:
    path = tmp_path / "test.toml"
    path.write_text('[tool.changelog]\nfrom = "v1.0.0"\n')
    data = _read_toml(path)
    assert data["tool"]["changelog"]["from"] == "v1.0.0"


def test_read_toml_missing(tmp_path: Path) -> None:
    assert _read_toml(tmp_path / "nonexistent.toml") == {}


def test_read_json_existing(tmp_path: Path) -> None:
    path = tmp_path / "test.json"
    path.write_text(json.dumps({"key": "value"}))
    assert _read_json(path) == {"key": "value"}


def test_read_json_missing(tmp_path: Path) -> None:
    assert _read_json(tmp_path / "nonexistent.json") == {}


# --- _load_dotenv ---


def test_load_dotenv_sets_env(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("TEST_VAR_DOTENV=hello\n")
    _load_dotenv(env_file)
    assert os.environ.get("TEST_VAR_DOTENV") == "hello"
    del os.environ["TEST_VAR_DOTENV"]


def test_load_dotenv_skips_comments(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\nKEY=value\n")
    _load_dotenv(env_file)
    assert os.environ.get("KEY") == "value"
    del os.environ["KEY"]


def test_load_dotenv_skips_no_equals(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("NOEQUALSSIGN\nKEY2=val\n")
    _load_dotenv(env_file)
    assert os.environ.get("KEY2") == "val"
    del os.environ["KEY2"]


def test_load_dotenv_strips_quotes(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("QUOTED=\"double\"\nSINGLE='single'\n")
    _load_dotenv(env_file)
    assert os.environ.get("QUOTED") == "double"
    assert os.environ.get("SINGLE") == "single"
    del os.environ["QUOTED"]
    del os.environ["SINGLE"]


def test_load_dotenv_missing_file(tmp_path: Path) -> None:
    _load_dotenv(tmp_path / ".env")  # should not raise


def test_load_dotenv_uses_setdefault(tmp_path: Path) -> None:
    os.environ["EXISTING_KEY"] = "original"
    env_file = tmp_path / ".env"
    env_file.write_text("EXISTING_KEY=new\n")
    _load_dotenv(env_file)
    assert os.environ["EXISTING_KEY"] == "original"
    del os.environ["EXISTING_KEY"]


# --- _load_config_payload ---


def test_load_config_payload_json(tmp_path: Path) -> None:
    config_file = tmp_path / "changelog.config.json"
    config_file.write_text(json.dumps({"from": "v1.0.0"}))
    payload = _load_config_payload(tmp_path)
    assert payload["from"] == "v1.0.0"


def test_load_config_payload_changelogrc(tmp_path: Path) -> None:
    config_file = tmp_path / ".changelogrc"
    config_file.write_text(json.dumps({"from": "v2.0.0"}))
    payload = _load_config_payload(tmp_path)
    assert payload["from"] == "v2.0.0"


def test_load_config_payload_toml(tmp_path: Path) -> None:
    config_file = tmp_path / "changelog.config.toml"
    config_file.write_text('[changelog]\nfrom = "v3.0.0"\n')
    payload = _load_config_payload(tmp_path)
    # TOML returns nested dict: {'changelog': {'from': 'v3.0.0'}}
    assert payload["changelog"]["from"] == "v3.0.0"


def test_load_config_payload_pyproject_fallback(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[tool.changelog]\nfrom = "v4.0.0"\n')
    payload = _load_config_payload(tmp_path)
    assert payload["from"] == "v4.0.0"


def test_load_config_payload_no_files(tmp_path: Path) -> None:
    payload = _load_config_payload(tmp_path)
    assert payload == {}


def test_load_config_payload_pyproject_no_tool(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "test"\n')
    payload = _load_config_payload(tmp_path)
    assert payload == {}


def test_load_config_payload_pyproject_tool_not_dict(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('tool = "string"\n')
    payload = _load_config_payload(tmp_path)
    assert payload == {}


# --- load_config ---


def test_load_config_defaults(tmp_path: Path) -> None:
    config = load_config(str(tmp_path))
    assert config.cwd == str(tmp_path)
    assert "feat" in config.types


def test_load_config_from_json(tmp_path: Path) -> None:
    config_file = tmp_path / "changelog.config.json"
    config_file.write_text(json.dumps({"from": "v1.0.0", "to": "HEAD"}))
    config = load_config(str(tmp_path))
    assert config.from_ref == "v1.0.0"
    assert config.to_ref == "HEAD"


def test_load_config_types_override(tmp_path: Path) -> None:
    config_file = tmp_path / "changelog.config.json"
    config_file.write_text(
        json.dumps({"types": {"custom": {"title": "Custom", "semver": "patch"}}})
    )
    config = load_config(str(tmp_path))
    assert "custom" in config.types


def test_load_config_scope_map(tmp_path: Path) -> None:
    config_file = tmp_path / "changelog.config.json"
    config_file.write_text(json.dumps({"scopeMap": {"core": "Core"}}))
    config = load_config(str(tmp_path))
    assert config.scope_map == {"core": "Core"}


def test_load_config_repo_string(tmp_path: Path) -> None:
    config_file = tmp_path / "changelog.config.json"
    config_file.write_text(json.dumps({"repo": "user/repo"}))
    config = load_config(str(tmp_path))
    assert config.repo == "user/repo"


def test_load_config_publish(tmp_path: Path) -> None:
    config_file = tmp_path / "changelog.config.json"
    config_file.write_text(
        json.dumps({"publish": {"tag": "next", "private": True, "args": ["--dry-run"]}})
    )
    config = load_config(str(tmp_path))
    assert config.publish.tag == "next"
    assert config.publish.private is True
    assert config.publish.args == ["--dry-run"]


def test_load_config_templates(tmp_path: Path) -> None:
    config_file = tmp_path / "changelog.config.json"
    config_file.write_text(
        json.dumps(
            {
                "templates": {
                    "commitMessage": "release: v{{newVersion}}",
                    "tagMessage": "tag: v{{newVersion}}",
                    "tagBody": "body: v{{newVersion}}",
                }
            }
        )
    )
    config = load_config(str(tmp_path))
    assert config.templates.commit_message == "release: v{{newVersion}}"


def test_load_config_no_authors(tmp_path: Path) -> None:
    config_file = tmp_path / "changelog.config.json"
    config_file.write_text(json.dumps({"noAuthors": True}))
    config = load_config(str(tmp_path))
    assert config.no_authors is True


def test_load_config_exclude_authors(tmp_path: Path) -> None:
    config_file = tmp_path / "changelog.config.json"
    config_file.write_text(json.dumps({"excludeAuthors": ["bot@example.com"]}))
    config = load_config(str(tmp_path))
    assert config.exclude_authors == ["bot@example.com"]


def test_load_config_hide_author_email(tmp_path: Path) -> None:
    config_file = tmp_path / "changelog.config.json"
    config_file.write_text(json.dumps({"hideAuthorEmail": True}))
    config = load_config(str(tmp_path))
    assert config.hide_author_email is True


def test_load_config_github_token_from_env(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test123")
    config = load_config(str(tmp_path))
    assert config.tokens.get("github") == "ghp_test123"


def test_load_config_changelogen_token_overrides(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CHANGELOGEN_TOKENS_GITHUB", "token_a")
    monkeypatch.setenv("GITHUB_TOKEN", "token_b")
    config = load_config(str(tmp_path))
    assert config.tokens["github"] == "token_a"


def test_load_config_existing_token_not_overridden(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "env_token")
    config_file = tmp_path / "changelog.config.json"
    config_file.write_text(json.dumps({"tokens": {"github": "config_token"}}))
    config = load_config(str(tmp_path))
    assert config.tokens["github"] == "config_token"


def test_load_config_output_false(tmp_path: Path) -> None:
    config_file = tmp_path / "changelog.config.json"
    config_file.write_text(json.dumps({"output": False}))
    config = load_config(str(tmp_path))
    assert config.output is False


def test_load_config_output_true(tmp_path: Path) -> None:
    config_file = tmp_path / "changelog.config.json"
    config_file.write_text(json.dumps({"output": True}))
    config = load_config(str(tmp_path))
    assert config.output is True


def test_load_config_sign_tags(tmp_path: Path) -> None:
    config_file = tmp_path / "changelog.config.json"
    config_file.write_text(json.dumps({"signTags": True}))
    config = load_config(str(tmp_path))
    assert config.sign_tags is True


def test_load_config_new_version(tmp_path: Path) -> None:
    config_file = tmp_path / "changelog.config.json"
    config_file.write_text(json.dumps({"newVersion": "2.0.0"}))
    config = load_config(str(tmp_path))
    assert config.new_version == "2.0.0"
