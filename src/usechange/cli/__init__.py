from __future__ import annotations

import importlib
import tempfile
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def _find_project_root(start_dir: Path) -> Path | None:
    current = start_dir.resolve()

    while True:
        if (current / "pyproject.toml").exists():
            return current
        if (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _resolve_usechange_prefix(project_root: Path) -> str:
    if (project_root / "src" / "usechange" / "cli" / "commands").exists():
        return "src/usechange"
    return ""


def _build_usecli_pyproject(project_root: Path) -> str:
    try:
        package_version = version("usechange")
    except PackageNotFoundError:
        package_version = "0.0.0"

    prefix = _resolve_usechange_prefix(project_root)
    base = f"{prefix}/" if prefix else ""

    return (
        "[tool.usecli]\n"
        'title = "useChange"\n'
        f'title_file = "{base}cli/themes/title.txt"\n'
        'title_font = "ansi_shadow"\n'
        'description = "Automated python change and release"\n'
        f'commands_dir = "{base}cli/commands"\n'
        f'templates_dir = "{base}cli/templates"\n'
        f'themes_dir = ["{base}cli/themes"]\n'
        'theme = "default"\n'
        "hide_init = true\n"
        "hide_inspire = true\n"
        "hide_make_command = true\n"
        'command_name = "usechange"\n'
        f'version = "{package_version}"\n'
    )


def _bootstrap_usecli_config() -> None:
    package_root = Path(__file__).resolve().parents[1]
    project_root = _find_project_root(package_root) or package_root
    pyproject_payload = _build_usecli_pyproject(project_root)
    temp_dir = Path(tempfile.mkdtemp(prefix="usechange-"))
    pyproject_path = temp_dir / "pyproject.toml"
    pyproject_path.write_text(pyproject_payload)
    manager_module = importlib.import_module("usecli.shared.config.manager")
    ConfigManager = getattr(manager_module, "ConfigManager")
    config_manager = ConfigManager(
        pyproject_path=pyproject_path,
        start_dir=package_root,
    )
    setattr(manager_module, "_config_manager", config_manager)


def main() -> None:
    _bootstrap_usecli_config()
    usecli_module = importlib.import_module("usecli")
    usecli_main = getattr(usecli_module, "main")
    usecli_main()


__all__ = ["main"]
