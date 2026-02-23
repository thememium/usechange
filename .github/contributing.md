# usechange Contributing Guide

Hi! Thanks for your interest in contributing to usechange. Before submitting a contribution, please read the guidelines below:

- [Code of Conduct](#code-of-conduct)
- [Issue Reporting Guidelines](#issue-reporting-guidelines)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Development Setup](#development-setup)
- [Scripts](#scripts)
- [Project Structure](#project-structure)

## Code of Conduct

This project and everyone participating in it is governed by a code of conduct. By participating, you are expected to uphold this code.

## Issue Reporting Guidelines

- Use the GitHub issue tracker to create new issues.
- Check for existing issues (open or closed) before filing a new one.
- Use issue templates when available.
- Provide a clear description of the problem and steps to reproduce.
- Include relevant environment information (Python version, OS, uv version).

## Pull Request Guidelines

### What kinds of Pull Requests are accepted?

- **Bug fixes** that address a clearly identified bug with a reproduction.
- **New features** that address a clear, widely applicable use case. Keep complexity proportional to the benefit.
- **Chores** like typos, comment improvements, build config, or CI config updates.
- **Documentation improvements** that clarify or expand existing docs.

We discourage refactors that are primarily stylistic. Please follow established conventions unless there is a clear, objective improvement.

### Pull Request Checklist

- Enable "Allow edits from maintainers".
- Reference an existing issue with `Fixes #123` or `Closes #123`.
- Add or update tests when fixing bugs or adding features.
- Keep PRs focused and small where possible.
- Make sure tests and checks pass: `uv run poe clean-full`.

PR titles should follow conventional commit standards:

- `feat:` new feature or functionality
- `fix:` bug fix
- `docs:` documentation changes
- `chore:` maintenance tasks or dependency updates
- `refactor:` refactoring without behavior changes
- `test:` adding or updating tests

## Development Setup

You will need:

- [Python](https://python.org) 3.10 or higher
- [uv](https://github.com/astral-sh/uv) for dependency management and running the project

After cloning the repo, run:

```bash
uv sync
```

Tools used by the project:

- [Python](https://python.org/) as the development language
- [usecli](https://github.com/thememium/usecli) for the CLI framework
- [pytest](https://docs.pytest.org/) for testing
- [ruff](https://docs.astral.sh/ruff/) for linting and formatting
- [isort](https://pycqa.github.io/isort/) for import sorting
- [deptry](https://github.com/fpgmaas/deptry) for dependency checks
- [ty](https://github.com/astral-sh/ty) for type checking

## Scripts

This project uses `poe` (poethepoet) for task management via `uv run poe <task>`.

- `uv run poe dev`
- `uv run poe test`
- `uv run poe clean`
- `uv run poe clean-full`
- `uv run poe sort`
- `uv run poe lint`
- `uv run poe format`
- `uv run poe deptry`
- `uv run poe typecheck`
- `uv run poe release`

### `uv run poe dev`

Run the CLI application:

```bash
uv run poe dev --help
```

This is equivalent to `uv run usechange --help`.

### `uv run poe test`

Run the test suite:

```bash
uv run poe test
```

You can also run specific tests:

```bash
# Run a specific test file
uv run pytest tests/test_semver.py -v

# Run a specific test
uv run pytest tests/test_semver.py::test_bump_version_major -v
```

### `uv run poe clean`

Quick clean - sorts imports and formats code:

```bash
uv run poe clean
```

### `uv run poe clean-full`

Full code quality check - runs all quality tools:

```bash
uv run poe clean-full
```

This runs:

- `isort` - Sort imports
- `ruff check` - Lint and auto-fix
- `ruff format` - Format code
- `deptry` - Check for dependency issues
- `ty check` - Type check

### `uv run poe sort`

Sort imports only:

```bash
uv run poe sort
```

### `uv run poe lint`

Lint code only:

```bash
uv run poe lint
```

### `uv run poe format`

Format code only:

```bash
uv run poe format
```

### `uv run poe deptry`

Check dependencies only:

```bash
uv run poe deptry
```

### `uv run poe typecheck`

Type check the codebase:

```bash
uv run poe typecheck
```

### `uv run poe release`

Run the release workflow:

```bash
uv run poe release
```

## Project Structure

```
├── src/usechange/                # Source code
│   ├── cli/                      # CLI implementation
│   │   ├── commands/             # Command implementations
│   │   ├── templates/            # CLI templates
│   │   └── themes/               # CLI themes
│   └── changelog/                # Changelog and release logic
│       └── cli/                  # Changelog CLI adapters
├── tests/                        # Test files
├── docs/                         # Documentation assets
└── .github/                      # GitHub config and templates
```

### Importing Code

When working within the codebase:

- Use absolute imports from the `usechange` package.
- Follow the import order: `__future__`, stdlib, third-party, local.
- Prefer `from __future__ import annotations` for forward references.

## Style Guidelines

- Keep functions focused and small when practical.
- Use type hints in new or modified code.
- Prefer specific exceptions over generic `Exception`.

## Credits

Thank you to all the people who have already contributed to usechange!

<a href="https://github.com/thememium/usechange/graphs/contributors"><img src="https://contrib.rocks/image?repo=thememium/usechange" /></a>
