---
name: usecli
description: Build, extend, and operate usecli-based Python CLIs. Use when a repository depends on usecli, contains a usecli.config.toml, or the user asks to add, change, or debug usecli commands, themes, JSON output, or packaging.
---

# usecli

`usecli` is a Python CLI framework. This document is the skill reference for the project CLI **`usecli`** (usecli 0.2.10).

> Run `usecli --help` for the live command list. Commands are discovered at runtime, so project-specific commands may exist that are not listed below.

## What usecli provides

- `BaseCommand` subclasses discovered automatically from the configured commands directory.
- Themed help for commands, arguments, and options.
- Automatic `--help`, `--json`, and `--interactive` support on every command.
- Prefix matching for command names (`usecli ma:sk` runs `make:skill`).
- Themed console output, prompts, menus, spinners, progress bars, and JSON output.
- Project scaffolding with the `usecli` binary (`init`, `make:command`,
  `make:theme`, `make:skill`, and `make:bundle`).

## Command conventions

- Single-level command: `def signature(self) -> str: return "status"`.
- Colon-grouped command: `def signature(self) -> str: return "db:migrate"` (displayed under `db:`).
- Nested subcommand: `def signature(self) -> str: return "spec show"` (invoked as `usecli spec show`).
- `handle()` may return any JSON-serializable value. In `--json` mode it becomes the `data` field.
- Human-facing output must use `usecli.console` or `print`; in JSON mode usecli routes it to stderr so stdout stays machine-readable.
- Do not call `sys.exit()` from `handle()` unless a non-zero exit status is required. Returning a value is preferred.

## Add a command

```sh
usecli make:command hello
```

This creates a command module in the project's commands directory. A minimal handwritten command looks like this:

```python
from __future__ import annotations

from usecli import Argument, BaseCommand, Option, console, theme


class HelloCommand(BaseCommand):
    def signature(self) -> str:
        return "hello"

    def description(self) -> str:
        return "Say hello"

    def handle(
        self,
        name: str = Argument(..., help="Who to greet"),
        loud: bool = Option(False, "--loud", "-l", help="Uppercase the greeting"),
    ) -> dict[str, str]:
        greeting = f"Hello, {name}!"
        if loud:
            greeting = greeting.upper()
        console.print(f"[bold {theme.SUCCESS}]{greeting}[/bold {theme.SUCCESS}]")
        return {"greeting": greeting}
```

Arguments and options can also be written with `typing.Annotated`, importing
`Argument` and `Option` from `usecli`:

```python
from typing import Annotated

from usecli import Argument, Option


def handle(
    self,
    name: Annotated[str, Argument(help="Who to greet")],
    loud: Annotated[bool, Option("--loud", "-l", help="Uppercase")] = False,
) -> None: ...
```

## Bundle a skill with this CLI

A project can ship its own Agent Skills. Put each skill in its own directory
under `paths.skills` (default `skills` beside `usecli.config.toml`):

```text
skills/
  deploy-checks/
    SKILL.md
```

Scaffold one with:

```sh
usecli make:skill deploy-checks --description "Check deployments"
```

Install the project's bundled skills with the project CLI. The default config
shows an interactive root option:

```sh
usecli --install-skills
```

Set `[usecli.commands] skill_install = "command"` to use the command form:

```sh
usecli skill:install
usecli skill:install --global
usecli skill:install --skill deploy-checks --agent claude,codex
usecli skill:install --interactive
usecli skill:install --list
```

A project CLI exposes the installer only when it has at least one bundled
skill. The project CLI installs project skills only; it never installs the
generated `usecli` skill.

The framework binary installs the generated `usecli` skill. The default option
is interactive; the command form exposes the full flag set:

```sh
usecli --install-skills
usecli skill:install
usecli skill:install --global
usecli skill:install --list
```

Installation is idempotent. Managed files carry a `<!-- usecli-skill: ... -->`
hash marker, so upgraded releases update their own files. Non-interactive
installs preserve locally edited files unless `--force` is passed. Interactive
installs replace local edits, matching `npx skills add`.

The public Python API is available too:

```python
from usecli.skills import Skill, install_skills

install_skills(
    [
        Skill(
            name="deploy-checks",
            description="Check deployments",
            content="---\nname: deploy-checks\ndescription: Check deployments\n---\n",
        )
    ],
    agents=["claude"],
    scope="project",
)
```

## Themes

Themes are TOML files. Create one with:

```sh
usecli make:theme dusk
```

Theme files live in the project's `paths.themes` directory. Reference colors through `usecli.theme` (`COLOR`) instead of hard-coding style strings:

```python
from usecli import console, theme

console.print(f"[{theme.PRIMARY}]Heading[/{theme.PRIMARY}]")
console.print(f"[{theme.SUCCESS}]Done[/{theme.SUCCESS}]")
```

## Interactive input and menus

```python
from usecli import Confirm, Menu, Prompt, console

name = Prompt.ask("Name", default="world")
port = Prompt.ask("Port", type="int", default=8000)
mode = Prompt.ask("Mode", choices=["dev", "prod"], default="dev")
if Confirm.ask("Continue?"):
    choice = Menu.select(["alpha", "beta", "gamma"], title="Pick one")
    choices = Menu.multi_select(["one", "two", "three"], title="Pick many")
    console.print(f"{name=} {port=} {mode=} {choice=} {choices=}")
```

`Prompt.ask(type=...)` accepts `"string"`, `"int"`, or `"float"`. Use `password=True` or `mask="*"` for secrets. Single-key prompts and menus should not be used in JSON mode; usecli raises `NonInteractiveError` and prompts resolve their declared defaults where possible.

## Progress

```python
from usecli import ProgressBar, Spinner

with Spinner("Loading") as spinner:
    load_data()
    spinner.update("Indexing")

with ProgressBar(total=len(items), description="Processing") as progress:
    for item in items:
        process(item)
        progress.advance()
```

Progress writes to stderr and is suppressed in JSON mode, with `quiet=True`, or when stderr is not a terminal.

## JSON mode

Every command inherits `--json` (it also works before the command name). stdout contains exactly one document:

```json
{"ok": true, "data": {"status": "ready"}}
```

Failures use a stable envelope and a non-zero exit status:

```json
{"ok": false, "error": {"type": "UsageError", "message": "...", "code": 2}}
```

Return data from `handle()` instead of printing JSON. Do not write to stdout in JSON mode.

## Configuration

- `usecli.config.toml` controls the CLI title, description, theme, and paths.
- `paths.commands` points at the command package (default `cli/commands`).
- `paths.templates` points at scaffolding templates (default `cli/templates`).
- `paths.themes` points at theme directories (default `cli/themes`).
- `pyproject.toml` exposes the project command through `[project.scripts]`.

Initialize a project with:

```sh
usecli init
```

## Packaging

Build a standalone executable with the optional PyInstaller extra:

```sh
usecli make:bundle --mode onefile -y
usecli make:bundle --mode onedir --zip -y
```

The bundle embeds `usecli.config.toml`, commands, templates, and themes. Keep resource paths relative to the project config so they resolve in both source and frozen modes.

## Completion and upgrades

```sh
usecli --show-completion
usecli --install-completion
usecli upgrade
```

## Commands

### `about`

Display detailed information about the application

```sh
usecli about --help
```

### `help`

Show help information

```sh
usecli help --help
```

### `init`

Initialize usecli in the current project

```sh
usecli init --help
```

- `--title` — Title for your CLI
- `--description` — Description for your CLI
- `--commands-dir` — Directory for custom commands
- `--templates-dir` — Directory for scaffolding templates
- `--themes-dir` — Directory for theme TOML files
- `--skills-dir` — Directory for bundled Agent Skills
- `--config-path` — Path for usecli.config.toml
- `--command-name, -c` — Command name for your CLI entry point
- `--force, -f` — Overwrite existing config without prompting
- `--theme` — Theme name (JSON mode only, default: 'default')
- `--title-font` — Figlet font for title (requires usecli[figlet]; JSON mode only, default: 'big')
- `--title-extra-top-space, --no-title-extra-top-space` — Add a blank line above the title banner (default: enabled)
- `--title-extra-bottom-space, --no-title-extra-bottom-space` — Add a blank line below the title banner (default: enabled)
- `--show-description, --no-show-description` — Show the description below the title banner (default: hidden with figlet, shown without)
- `--show-version, --no-show-version` — Show the version in the title banner (default: hidden with figlet, shown without)
- `--install-skill, --no-install-skill` — Install the usecli skill for coding agents

### `inspire`

Show a random inspirational quote

```sh
usecli inspire --help
```

### `make:command`

Create a new CLI command

```sh
usecli make:command --help
```

- `<NAME>` — The name of the command

### `make:skill`

Create a new bundled skill

```sh
usecli make:skill --help
```

- `<NAME>` — Skill name (lowercase-with-hyphens)
- `--description, -d` — Short description used in the skill frontmatter

### `make:theme`

Create a new theme file

```sh
usecli make:theme --help
```

- `<NAME>` — Theme config name

### `upgrade`

Upgrade the application to the latest version

```sh
usecli upgrade --help
```

- `--check` — Only check for updates; do not install anything.
- `--force` — Upgrade even when already up to date and skip the confirmation prompt.

<!-- usecli-skill: name=usecli hash=feff69df4c0b3d49978fe8d67bda88b16de9e99176c43c81861eea7abbf7d95f -->
