<a name="readme-top"></a>

<div align="center">
  <a href="https://github.com/thememium/usechange">
    <img src="https://raw.githubusercontent.com/thememium/usechange/refs/heads/master/docs/images/usechange-logo-dark-bg.png" alt="useChange" width="520" height="162">
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

usechange provides a short alias and command shortcuts:

- `usechange` and `change` are equivalent.
- `changelog` also supports the `log` alias.

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
change log --write
```

### Interactive release workflow

```sh
change release
```

### Sync the latest release to GitHub

```sh
change github release
```

### Interactive changelog preview

Example prompt for selecting optional changelog flags:

```
Select optional flags (space to select, enter to confirm):
> [ ] --from - Start commit reference
  [ ] --to - End commit reference
  [ ] --dir - Path to a git repository
  [ ] --clean [bool] - Ensure working directory is clean
  [ ] --output - Changelog file to write
  [ ] --write [bool] - Write changelog to CHANGELOG.md
  [ ] --no-output [bool] - Do not write a changelog file
  [ ] --noAuthors [bool] - Skip contributors section
  [ ] --noDate [bool] - Omit date from header
  [ ] --noEmojis [bool] - Omit emojis from headers
  [ ] --hideAuthorEmail [bool] - Hide author email if no username is found
  [ ] --bump [bool] - Determine and update version
  [ ] -r - Release as a specific version
  [ ] --release [bool] - Bump, tag, and release
  [ ] --no-commit [bool] - Skip release commit
  [ ] --no-tag [bool] - Skip release tag
  [ ] --push [bool] - Push commits and tags
  [ ] --no-github [bool] - Skip GitHub release sync
  [ ] --publish [bool] - Publish after generating
  [ ] --publishTag - Publish with a custom tag
  [ ] --nameSuffix - Append suffix to package name
  [ ] --versionSuffix - Append suffix to version
  [ ] --canary - Shortcut for --bump and --versionSuffix
  [ ] --major [bool] - Force major bump
  [ ] --minor [bool] - Force minor bump
  [ ] --patch [bool] - Force patch bump
  [ ] --premajor - Force premajor bump
  [ ] --preminor - Force preminor bump
  [ ] --prepatch - Force prepatch bump
  [ ] --prerelease - Force prerelease bump
Press <space>, <tab> for multi-selection and <enter> to accept
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE -->

## Usage

### Generate changelog

```sh
change log --from v0.1.0 --to HEAD --output CHANGELOG.md
```

### Version bumping

```sh
change log --bump --write
change log --major --write
```

### Release workflow

```sh
change release --yes
```

### GitHub release sync

```sh
change github release 0.2.0
change gh release all
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
