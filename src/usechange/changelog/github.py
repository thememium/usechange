from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GitHubReleaseRequest:
    version: str
    body: str
    token: str | None
    repo: str | None


def _load_gh_token() -> str | None:
    gh_hosts = Path.home() / ".config" / "gh" / "hosts.yml"
    if not gh_hosts.exists():
        return None
    in_section = False
    for raw_line in gh_hosts.read_text().splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if not line.startswith(" ") and line.endswith(":"):
            in_section = line.strip() == "github.com:"
            continue
        if in_section and "oauth_token:" in line:
            _, token = line.split("oauth_token:", 1)
            return token.strip().strip('"').strip("'")
    return None


def _request_json(
    url: str, token: str | None, method: str = "GET", payload: dict | None = None
) -> dict | None:
    data = None
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "usechange",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
            if not body:
                return None
            return json.loads(body)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise RuntimeError(error.read().decode("utf-8") or str(error)) from error


def _normalize_tag(version: str) -> str:
    if version.startswith("v"):
        return version
    return f"v{version}"


def sync_release(request: GitHubReleaseRequest) -> bool:
    if not request.repo:
        raise RuntimeError("Missing repository for GitHub release")

    token = (
        request.token
        or os.environ.get("CHANGELOGEN_TOKENS_GITHUB")
        or os.environ.get("GITHUB_TOKEN")
        or os.environ.get("GH_TOKEN")
        or _load_gh_token()
    )
    if not token:
        raise RuntimeError("Missing GitHub token")

    tag = _normalize_tag(request.version)
    base_url = f"https://api.github.com/repos/{request.repo}"
    existing = _request_json(f"{base_url}/releases/tags/{tag}", token)

    payload = {
        "tag_name": tag,
        "name": tag,
        "body": request.body,
        "draft": False,
        "prerelease": "-" in request.version,
    }

    if existing and "id" in existing:
        release_id = existing["id"]
        _request_json(
            f"{base_url}/releases/{release_id}", token, method="PATCH", payload=payload
        )
        return True

    _request_json(f"{base_url}/releases", token, method="POST", payload=payload)
    return True
