#!/usr/bin/env bash
set -e

read -p "Continue with release? [y/N] " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    npx changelogen@latest --bump
    VERSION=$(node -p "require('./package.json').version")
    uv version "$VERSION"
    uv sync
    uv lock
    git add CHANGELOG.md package.json pyproject.toml uv.lock
    git commit -m "chore(uv): update version"
    git tag "v$VERSION"
    git push
    git push origin "v$VERSION"
    NOTES_FILE=$(mktemp)
    VERSION="$VERSION" uv run python - <<'PY' > "$NOTES_FILE"
import os
from pathlib import Path

version = os.environ["VERSION"]
heading = f"## v{version}"
lines = Path("CHANGELOG.md").read_text().splitlines()

start = None
for idx, line in enumerate(lines):
    if line.strip() == heading:
        start = idx
        break

if start is None:
    raise SystemExit(f"Missing changelog entry for {heading}")

end = None
for idx in range(start + 1, len(lines)):
    if lines[idx].startswith("## "):
        end = idx
        break

section = lines[start:end]
print("\n".join(section).rstrip())
PY
    TARGET_SHA=$(git rev-parse "v$VERSION")
    if gh release view "v$VERSION" >/dev/null 2>&1; then
        gh release edit "v$VERSION" --notes-file "$NOTES_FILE"
    else
        gh release create "v$VERSION" --target "$TARGET_SHA" --notes-file "$NOTES_FILE"
    fi
else
    echo "Release cancelled."
fi
