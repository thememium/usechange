"""Configuration manager for useChange CLI.

Handles loading, merging, and accessing global and local configuration files.
Global config is located at ~/.config/usechange/config.yaml.
Local config is located at ./.usechange/config.yaml and overrides global values.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from usechange.cli.core.exceptions.config import UsechangeConfigError


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dictionaries, with override taking precedence.

    Args:
        base: The base dictionary.
        override: The dictionary to merge on top.

    Returns:
        A new dictionary containing the merged result.
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class ConfigManager:
    """Manages useChange configuration with global and local file support.

    Configuration is loaded from two sources:
    1. Global config: ~/.config/usechange/config.yaml
    2. Local config: ./.usechange/config.yaml (overrides global values)

    Local configuration values take precedence over global ones.
    If neither config exists, sensible defaults are returned.

    Attributes:
        global_config_path: Path to the global configuration file.
        local_config_path: Path to the local (project-specific) configuration file.
        _config: The merged configuration dictionary.
    """

    # Default configuration values
    DEFAULT_CONFIG: dict[str, Any] = {
        "environment": "prod",
        "logging": {
            "level": "info",
            "file_enabled": False,
            "file_path": "usechange.log",
        },
        "features": {
            "auto_update_check": True,
            "analytics": False,
        },
        "defaults": {
            "editor": os.environ.get("EDITOR", "vim"),
            "assistant": "auto",
        },
    }

    def __init__(
        self,
        global_config_path: Path | None = None,
        local_config_path: Path | None = None,
    ) -> None:
        """Initialize the configuration manager.

        Args:
            global_config_path: Optional path to global config. Defaults to
                ~/.config/usechange/config.yaml.
            local_config_path: Optional path to local config. Defaults to
                ./.usechange/config.yaml.
        """
        if global_config_path is None:
            global_config_path = Path.home() / ".config" / "usechange" / "config.yaml"
        if local_config_path is None:
            local_config_path = Path.cwd() / ".usechange" / "config.yaml"

        self.global_config_path: Path = global_config_path
        self.local_config_path: Path = local_config_path
        self._config: dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load and merge global and local configurations."""
        # Start with defaults
        self._config = self.DEFAULT_CONFIG.copy()

        # Load global config if it exists
        if self.global_config_path.exists():
            try:
                global_config = self._load_yaml(self.global_config_path)
                self._config = _deep_merge(self._config, global_config)
            except (yaml.YAMLError, OSError) as e:
                raise UsechangeConfigError(
                    f"Failed to load global config: {e}",
                    config_file=str(self.global_config_path),
                ) from e

        # Load local config if it exists (takes precedence)
        if self.local_config_path.exists():
            try:
                local_config = self._load_yaml(self.local_config_path)
                self._config = _deep_merge(self._config, local_config)
            except (yaml.YAMLError, OSError) as e:
                raise UsechangeConfigError(
                    f"Failed to load local config: {e}",
                    config_file=str(self.local_config_path),
                ) from e

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        """Load YAML file and return parsed dictionary.

        Args:
            path: Path to the YAML file.

        Returns:
            Parsed YAML content as a dictionary.

        Raises:
            yaml.YAMLError: If the YAML file is malformed.
            OSError: If the file cannot be read.
        """
        with open(path, encoding="utf-8") as f:
            content = yaml.safe_load(f)
            if content is None:
                return {}
            if not isinstance(content, dict):
                raise yaml.YAMLError(f"Config file {path} must contain a YAML object")
            return content

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation.

        Args:
            key: The configuration key in dot notation (e.g., "logging.level").
            default: The default value to return if the key is not found.

        Returns:
            The configuration value, or the default if not found.

        Example:
            >>> config.get("environment")
            "dev"
            >>> config.get("logging.level")
            "info"
        """
        keys = key.split(".")
        value = self._config
        for k in keys:
            if not isinstance(value, dict) or k not in value:
                return default
            value = value[k]
        return value

    def get_all(self) -> dict[str, Any]:
        """Get the complete merged configuration.

        Returns:
            A dictionary containing all configuration values.
        """
        return self._config.copy()

    def is_dev(self) -> bool:
        """Check if running in development environment.

        Returns:
            True if environment is "dev", False otherwise.
        """
        return self.get("environment", "prod") == "dev"

    def is_prod(self) -> bool:
        """Check if running in production environment.

        Returns:
            True if environment is "prod", False otherwise.
        """
        return self.get("environment", "prod") == "prod"

    def reload(self) -> None:
        """Reload configuration from disk.

        Useful when config files may have changed externally.
        """
        self._load_config()

    @property
    def global_config_exists(self) -> bool:
        """Check if global configuration file exists.

        Returns:
            True if the global config file exists, False otherwise.
        """
        return self.global_config_path.exists()

    @property
    def local_config_exists(self) -> bool:
        """Check if local configuration file exists.

        Returns:
            True if the local config file exists, False otherwise.
        """
        return self.local_config_path.exists()


# Singleton instance for global use
_config_manager: ConfigManager | None = None


def get_config() -> ConfigManager:
    """Get the global ConfigManager instance.

    Returns:
        The singleton ConfigManager instance, creating it if necessary.
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def reset_config() -> None:
    """Reset the global ConfigManager instance.

    Forces a reload of configuration on next access. Useful for testing.
    """
    global _config_manager
    _config_manager = None
