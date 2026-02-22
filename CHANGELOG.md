# Changelog

## v0.1.5 (2026-02-22)

### 🚀 Enhancements

- **changelog**: add `update_versions` flag to optionally skip version bump ([5563a40](https://github.com/thememium/usechange/commit/5563a40fa91e59de597008c4b547e18e6ac2006c))

### 💅 Refactors

- **cli**: rename GhReleaseCommand to GithubReleaseCommand and add alias ([a504f68](https://github.com/thememium/usechange/commit/a504f68ffdf7567a46cdf2087296240bf7346a50))

### 🏡 Chore

- **deps**: bump tomli to >=2.4.0 and usecli to >=0.1.32 ([b4185f4](https://github.com/thememium/usechange/commit/b4185f4b26df7582e21ab6c53873aa73db227be0))
- **pyproject**: hide make command by default ([caa8b82](https://github.com/thememium/usechange/commit/caa8b82f4fb895643ce658e1b205629b187be04b))

### Contributors

- Edward Boswell <thememium@gmail.com>

[Compare changes](https://github.com/thememium/usechange/compare/v0.1.4...HEAD)

## v0.1.4 (2026-02-22)

### 🩹 Fixes

- **release_command**: set Confirm.ask default to false to require explicit confirmation ([8f9d2a4](https://github.com/thememium/usechange/commit/8f9d2a49dd7bcbad9962552e2617b29b5223b93d))

### 💅 Refactors

- **release**: drop package.json handling and related code ([b4d06b9](https://github.com/thememium/usechange/commit/b4d06b9491b7e84094eb317204396eeb6ca8b75c))

### Contributors

- Edward Boswell <thememium@gmail.com>

[Compare changes](https://github.com/thememium/usechange/compare/v0.1.3...HEAD)

## v0.1.3 (2026-02-22)

### 🚀 Enhancements

- **release**: read version from package.json, add it to git, and use gh CLI for releases ([96e7d91](https://github.com/thememium/usechange/commit/96e7d9149f776ccae05e3b0e2e7ae61ee6ff6f4f))
- **changelog**: sync versions in package.json and pyproject.toml on bump ([789a957](https://github.com/thememium/usechange/commit/789a95798c1e13bce2c4a16a2df7270bff5463a7))

### 🩹 Fixes

- **release**: use startswith for heading detection in release notes extraction ([a2b3021](https://github.com/thememium/usechange/commit/a2b302126dcecb41a5cbc0d7b0ef267b7d1caa3b))

### 🏡 Chore

- **release**: avoid duplicate git tags on release ([eb6c775](https://github.com/thememium/usechange/commit/eb6c7756a2320b940eab1f5f5fc2ff83c6ccafc3))

### 🎨 Styles

- **usechange/changelog/cli/default.py**: reorder imports for consistency ([54878e2](https://github.com/thememium/usechange/commit/54878e25a05375b7c9d0e982a8fe8fc3d4c77563))

### Contributors

- Edward Boswell <thememium@gmail.com>

[Compare changes](https://github.com/thememium/usechange/compare/v0.1.1...HEAD)

## v0.1.2 (2026-02-22)

### 🚀 Enhancements

- **release**: read version from package.json, add it to git, and use gh CLI for releases ([96e7d91](https://github.com/thememium/usechange/commit/96e7d9149f776ccae05e3b0e2e7ae61ee6ff6f4f))
- **changelog**: sync versions in package.json and pyproject.toml on bump ([789a957](https://github.com/thememium/usechange/commit/789a95798c1e13bce2c4a16a2df7270bff5463a7))

### 🏡 Chore

- **release**: avoid duplicate git tags on release ([eb6c775](https://github.com/thememium/usechange/commit/eb6c7756a2320b940eab1f5f5fc2ff83c6ccafc3))

### 🎨 Styles

- **usechange/changelog/cli/default.py**: reorder imports for consistency ([54878e2](https://github.com/thememium/usechange/commit/54878e25a05375b7c9d0e982a8fe8fc3d4c77563))

### Contributors

- Edward Boswell <thememium@gmail.com>

[Compare changes](https://github.com/thememium/usechange/compare/v0.1.1...HEAD)

## v0.1.1 (2026-02-22)

### 🏡 Chore

- **release**: avoid duplicate git tags on release ([eb6c775](https://github.com/thememium/usechange/commit/eb6c7756a2320b940eab1f5f5fc2ff83c6ccafc3))

### Contributors

- Edward Boswell <thememium@gmail.com>

[Compare changes](https://github.com/thememium/usechange/compare/v0.1.1...HEAD)
