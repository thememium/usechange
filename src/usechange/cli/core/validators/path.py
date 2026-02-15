"""Parameter validation callbacks for filesystem paths."""

from __future__ import annotations

import os

from usechange.cli.core.exceptions import UsechangeBadParameter


def validate_path_exists(value: str) -> str:
    """Validate that a file or directory path exists.

    Args:
        value: The path to validate.

    Returns:
        The validated path.

    Raises:
        UsechangeBadParameter: If the path does not exist.
    """
    if not os.path.exists(value):
        raise UsechangeBadParameter(f"Path does not exist: {value}", param_hint="--path")

    return value


def validate_file_exists(value: str) -> str:
    """Validate that a file exists.

    Args:
        value: The file path to validate.

    Returns:
        The validated file path.

    Raises:
        UsechangeBadParameter: If the file does not exist or is not a file.
    """
    if not os.path.exists(value):
        raise UsechangeBadParameter(f"File does not exist: {value}", param_hint="--file")

    if not os.path.isfile(value):
        raise UsechangeBadParameter(f"Path is not a file: {value}", param_hint="--file")

    return value


def validate_directory_exists(value: str) -> str:
    """Validate that a directory exists.

    Args:
        value: The directory path to validate.

    Returns:
        The validated directory path.

    Raises:
        UsechangeBadParameter: If the directory does not exist or is not a directory.
    """
    if not os.path.exists(value):
        raise UsechangeBadParameter(
            f"Directory does not exist: {value}", param_hint="--dir"
        )

    if not os.path.isdir(value):
        raise UsechangeBadParameter(
            f"Path is not a directory: {value}", param_hint="--dir"
        )

    return value
