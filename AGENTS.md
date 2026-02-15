# AGENTS.md - useChange CLI

Agentic coding guidelines for the useChange project.

## Build / Lint / Test Commands

```bash
# Run CLI in development
uv run usechange

# Run all tests
uv run poe test
# or
uv run pytest tests/ -v

# Run single test file
uv run pytest tests/test_file.py -v

# Run single test function
uv run pytest tests/test_file.py::test_function_name -v

# Full check (isort + lint + format + deptry + typecheck)
uv run poe clean-full

# Quick clean (isort + format only)
uv run poe clean

# Individual tools
uv run poe sort       # isort
uv run poe lint       # ruff check
uv run poe format     # ruff format
uv run poe typecheck  # ty
uv run poe deptry     # dependency check
```

## Code Style Guidelines

### Python Version
- Python 3.12+
- All files must include: `from __future__ import annotations`

### Imports
```python
from __future__ import annotations  # First line always

# Standard library
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

# Third-party
import typer
from rich.console import Console

# Local (absolute imports only)
from usechange.cli.config.colors import COLOR
from usechange.shared.config.globals import PACKAGE_ROOT

# TYPE_CHECKING block for circular imports
if TYPE_CHECKING:
    from click.core import Context
```

### Type Hints
- Use type hints on all function signatures
- Use `| None` instead of `Optional`
- Use `list[str]` instead of `List[str]`
- Use `dict[str, Any]` instead of `Dict[str, Any]`
- Return type `-> None` for procedures
- Use `typing.Final` for constants
- Use `typing.final` decorator for final classes/methods

### Naming Conventions
- `snake_case` for functions, methods, variables
- `PascalCase` for classes
- `SCREAMING_SNAKE_CASE` for constants
- Private methods: `_leading_underscore`
- Abstract base classes should be marked with `ABC`

### Error Handling
- Use custom exceptions in `usechange.cli.core.exceptions`
- Base class: `UsechangeError` (extends `ClickException`)
- Use `UsechangeBadParameter` for invalid CLI parameters
- Use `UsechangeUsageError` for usage errors
- Always call `.show()` on exceptions before exiting
- Exit codes: use `sys.exit(exit_code)` after showing error

### CLI Patterns
- Commands inherit from `BaseCommand` in `usechange.cli.core.base_command`
- Implement `signature()`, `description()`, `handle()` methods
- Use `typer.Argument()` and `typer.Option()` for parameters
- Use Rich console for output: `from rich.console import Console`
- Use color constants from `usechange.cli.config.colors`

### Docstrings
```python
"""Short description.

Longer description if needed.

Args:
    param1: Description of param1
    param2: Description of param2

Returns:
    Description of return value

Raises:
    ExceptionType: When this happens
"""
```

### Code Organization
```
src/usechange/
├── __init__.py          # CLI entry point, app setup
├── cli/
│   ├── commands/        # Command implementations
│   │   ├── defaults/    # Built-in commands
│   │   └── custom/      # User-generated commands
│   ├── config/          # Configuration, colors
│   ├── core/            # Base classes, validators, exceptions
│   ├── services/        # Business logic services
│   ├── templates/       # Jinja2 templates
│   └── utils/           # Utility functions
└── shared/
    └── config/          # Global config, paths
```

### Key Files
- Entry point: `src/usechange/__init__.py`
- Base command: `src/usechange/cli/core/base_command.py`
- Colors: `src/usechange/cli/config/colors.py`
- Exceptions: `src/usechange/cli/core/exceptions/`
- Global paths: `src/usechange/shared/config/globals.py`

## Rules
- Prefer absolute imports over relative
- Add type hints to all public functions
- Use Rich console for all CLI output
- Follow existing command patterns when adding new commands
- Run `uv run poe clean` before committing
- Keep functions focused and under 50 lines when possible
