from __future__ import annotations

import importlib


def test_package_imports_smoke() -> None:
    module = importlib.import_module("usechange.changelog")
    assert hasattr(module, "run_changelog")
    assert hasattr(module, "run_github_release")


def test_cli_commands_smoke() -> None:
    changelog_module = importlib.import_module(
        "usechange.cli.commands.changelog_command"
    )
    release_module = importlib.import_module("usechange.cli.commands.release_command")

    assert hasattr(changelog_module, "ChangelogCommand")
    assert callable(changelog_module.ChangelogCommand.signature)
    assert hasattr(release_module, "ReleaseCommand")
    assert callable(release_module.ReleaseCommand.signature)
