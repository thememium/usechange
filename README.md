<a name="readme-top"></a>

<div align="center">
  <a href="https://github.com/thememium/usechange">
    <img src="docs/images/usechange-logo-dark-bg.png" alt="useChange" width="520" height="162">
  </a>

  <p align="center">
    <a href="#table-of-contents"><strong>Explore the Documentation »</strong></a>
    <br />
    <a href="https://github.com/thememium/usechange/issues">Report Bug</a>
    ·
    <a href="https://github.com/thememium/usechange/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->

<a name="table-of-contents"></a>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about">About</a></li>
    <li><a href="#quick-start">Quick Start</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#development">Development</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

<!-- ABOUT -->

## About

usechange is a Python CLI for generating changelogs and release notes from
Conventional Commits. It reads git history between refs, groups commits by type,
renders Markdown release notes, and can update version numbers based on semantic
versioning rules.

It gives you:

- **Changelog generation** - Render release notes and optionally write to
  CHANGELOG.md.
- **Semver bumping** - Determine version bumps from commit types and breaking
  changes.
- **Release workflows** - Tag and publish using uv and gh.
- **GitHub sync** - Sync release notes to GitHub releases.
- **Repo metadata** - Create commit and compare links automatically.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- QUICK START -->

## Quick Start

### Install usechange with uv (recommended)

```sh
uv add usechange
```

### Install with pip (alternative)

```sh
pip install usechange
```

### Generate a changelog

```sh
usechange changelog --write
```

### Sync the latest release to GitHub

```sh
usechange github release
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE -->

## Usage

### Generate changelog

```sh
usechange changelog --from v0.1.0 --to HEAD --output CHANGELOG.md
```

### Version bumping

```sh
usechange changelog --bump --write
usechange changelog --major --write
```

### Release workflow

```sh
usechange release --yes
```

### GitHub release sync

```sh
usechange github release 0.2.0
usechange github release all
```

### Configuration

usechange reads configuration from one of the following:

- changelog.config.json
- .changelogrc
- changelog.config.toml
- pyproject.toml under [tool.changelog]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- DEVELOPMENT -->

## Development

Common tasks:

```sh
uv run poe test
uv run poe lint
uv run poe format
uv run poe typecheck
uv run poe clean-full
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->

## Contributing

Quick workflow:

1. Fork and branch: `git checkout -b feature/name`
2. Make changes
3. Run checks: `uv run poe clean-full`
4. Commit and push
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->

## License

License not yet specified in this repository.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<div align="center">
  <p>
    <sub>Built by <a href="https://github.com/thememium">thememium</a></sub>
  </p>
</div>
