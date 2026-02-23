# Changelog

## v0.1.8 (2026-02-23)

### 🚀 Enhancements

- **release**: auto‑bump version when existing tag or version present ([0c461bc](https://github.com/thememium/usechange/commit/0c461bcebef39f08cf17ffd3e63bde5b701f7c49))

### 🤖 CI

- **publish**: add workflow to publish package on release ([53c02fe](https://github.com/thememium/usechange/commit/53c02fedb477efe1a128cb8e7f70b98609aa28bc))

### Contributors

- Edward Boswell <thememium@gmail.com>

[Compare changes](https://github.com/thememium/usechange/compare/v0.1.7...HEAD)

## v0.1.7 (2026-02-23)

### 🚀 Enhancements

- **changelog_command**: add "log" alias to ChangelogCommand ([49a6b88](https://github.com/thememium/usechange/commit/49a6b889030cb55d1b53dbc8b4a96903f9326188))
- **changelog**: support optional output file and return content when not written ([b604102](https://github.com/thememium/usechange/commit/b6041022e78642ea650a84c978f78cd9bbdc63c2))

### 📖 Documentation

- **issue-template**: add GitHub bug report template ([569b426](https://github.com/thememium/usechange/commit/569b426cd78942b5c23fb80574f83061266ae8dd))
- **contributing**: add comprehensive contributing guide ([8487cb7](https://github.com/thememium/usechange/commit/8487cb7fed1a88eae1f8d11f736d0c10f623c25c))
- add MIT LICENSE file ([5d2a89c](https://github.com/thememium/usechange/commit/5d2a89c693c6dfa454ed341733529d4fe298fbb4))
- **security**: add SECURITY.md with vulnerability reporting guidelines ([e10a6a6](https://github.com/thememium/usechange/commit/e10a6a636eeb6c7a34566a4aff087fa45afd6578))
- **readme**: replace relative logo path with absolute raw GitHub URL ([7024dc5](https://github.com/thememium/usechange/commit/7024dc5af41f1fa7a6a303539d20dbcee1d1832e))
- add comprehensive README and project logo ([5e3590e](https://github.com/thememium/usechange/commit/5e3590e598ea103e2def4cbc55045b2c817cafc3))

### 📦 Build

- **pyproject**: add metadata, scripts, and migrate to uv_build ([d0dd70a](https://github.com/thememium/usechange/commit/d0dd70ac79defcd725bf546268e4af1650bc9c27))

### 🏡 Chore

- **usechange**: add __init__.py to mark directory as a package ([3930ebb](https://github.com/thememium/usechange/commit/3930ebb83d0dbe0a883684ceb0883bb12800d800))

### Contributors

- Edward Boswell <thememium@gmail.com>

[Compare changes](https://github.com/thememium/usechange/compare/v0.1.6...HEAD)

## v0.1.6 (2026-02-22)

### 🚀 Enhancements

- **cli**: add tag existence check to release command ([c6e1863](https://github.com/thememium/usechange/commit/c6e1863f5a2eddeb9fa257d8dc6e0643e6e3c971))

### 🏡 Chore

- **pyproject**: update release script to use `uv run` instead of a bash command ([efa7dfb](https://github.com/thememium/usechange/commit/efa7dfb5b6e44de71d42cedb908a6df0a6788190))
- **scripts**: delete legacy release.sh script ([28727a4](https://github.com/thememium/usechange/commit/28727a464ca724a90c1eb091981d12a0954b3610))

### Contributors

- Edward Boswell <thememium@gmail.com>

[Compare changes](https://github.com/thememium/usechange/compare/v0.1.5...HEAD)

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
