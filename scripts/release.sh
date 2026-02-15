#!/usr/bin/env bash
set -e

read -p "Continue with release? [y/N] " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    npx changelogen@latest --release
    qq -r .version package.json | xargs uv version
    git add .
    git commit -m "chore(uv): update version"
    git push
else
    echo "Release cancelled."
fi
