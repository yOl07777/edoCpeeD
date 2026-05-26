"""Bridge session create/fetch/archive/title helpers."""

from __future__ import annotations

import re
from typing import Any, Callable

import httpx

from .bridgeConfig import getBridgeAccessToken, getBridgeBaseUrl
from .sessionIdCompat import toCompatSessionId


def _headers(token: str, org_uuid: str | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    if org_uuid:
        headers["x-organization-uuid"] = org_uuid
    return headers


def _parse_github_repo(url: str) -> tuple[str, str] | None:
    patterns = [
        r"github\.com[:/](?P<owner>[^/\s]+)/(?P<name>[^/\s.]+)(?:\.git)?",
        r"^(?P<owner>[^/\s]+)/(?P<name>[^/\s.]+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group("owner"), match.group("name")
    return None


def _git_context(gitRepoUrl: str | None, branch: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not gitRepoUrl:
        return [], []
    parsed = _parse_github_repo(gitRepoUrl)
    if not parsed:
        return [], []
    owner, name = parsed
    revision = branch or None
    return (
        [{"type": "git_repository", "url": f"https://github.com/{owner}/{name}", **({"revision": revision} if revision else {})}],
        [{"type": "git_repository", "git_info": {"type": "github", "repo": f"{owner}/{name}", "branches": [f"deepseek/{branch or 'task'}"]}}],
    )


async def createBridgeSession(
    opts: dict[str, Any] | None = None,
    *,
    environmentId: str | None = None,
    title: str | None = None,
    events: list[dict[str, Any]] | None = None,
    gitRepoUrl: str | None = None,
    branch: str = "",
    baseUrl: str | None = None,
    getAccessToken: Callable[[], str | None] | None = None,
    permissionMode: str | None = None,
    orgUUID: str | None = None,
    client: httpx.AsyncClient | None = None,
) -> str | None:
    data = dict(opts or {})
    environmentId = environmentId or data.get("environmentId")
    title = title if title is not None else data.get("title")
    events = events if events is not None else data.get("events", [])
    gitRepoUrl = gitRepoUrl if gitRepoUrl is not None else data.get("gitRepoUrl")
    branch = branch or data.get("branch", "")
    baseUrl = baseUrl or data.get("baseUrl") or getBridgeBaseUrl()
    getAccessToken = getAccessToken or data.get("getAccessToken")
    permissionMode = permissionMode or data.get("permissionMode")
    orgUUID = orgUUID or data.get("orgUUID")
    client = client or data.get("client")

    token = getAccessToken() if getAccessToken else getBridgeAccessToken()
    if not token or not environmentId:
        return None
    sources, outcomes = _git_context(gitRepoUrl, branch)
    body: dict[str, Any] = {
        "events": events or [],
        "session_context": {"sources": sources, "outcomes": outcomes, "model": data.get("model", "deepseek-chat")},
        "environment_id": environmentId,
        "source": "remote-control",
    }
    if title is not None:
        body["title"] = title
    if permissionMode:
        body["permission_mode"] = permissionMode
    owns_client = client is None
    http = client or httpx.AsyncClient(timeout=10.0)
    try:
        response = await http.post(f"{baseUrl.rstrip('/')}/v1/sessions", json=body, headers=_headers(token, orgUUID))
        if response.status_code not in {200, 201}:
            return None
        parsed = response.json()
    except (httpx.HTTPError, ValueError):
        return None
    finally:
        if owns_client:
            await http.aclose()
    session_id = parsed.get("id") if isinstance(parsed, dict) else None
    return session_id if isinstance(session_id, str) else None


async def getBridgeSession(
    sessionId: str,
    opts: dict[str, Any] | None = None,
    *,
    baseUrl: str | None = None,
    getAccessToken: Callable[[], str | None] | None = None,
    orgUUID: str | None = None,
    client: httpx.AsyncClient | None = None,
) -> dict[str, Any] | None:
    opts = opts or {}
    baseUrl = baseUrl or opts.get("baseUrl") or getBridgeBaseUrl()
    getAccessToken = getAccessToken or opts.get("getAccessToken")
    orgUUID = orgUUID or opts.get("orgUUID")
    client = client or opts.get("client")
    token = getAccessToken() if getAccessToken else getBridgeAccessToken()
    if not token:
        return None
    owns_client = client is None
    http = client or httpx.AsyncClient(timeout=10.0)
    try:
        response = await http.get(f"{baseUrl.rstrip('/')}/v1/sessions/{sessionId}", headers=_headers(token, orgUUID))
        if response.status_code != 200:
            return None
        data = response.json()
    except (httpx.HTTPError, ValueError):
        return None
    finally:
        if owns_client:
            await http.aclose()
    return data if isinstance(data, dict) else None


async def archiveBridgeSession(sessionId: str, opts: dict[str, Any] | None = None, **kwargs: Any) -> None:
    opts = {**(opts or {}), **kwargs}
    baseUrl = opts.get("baseUrl") or getBridgeBaseUrl()
    getAccessToken = opts.get("getAccessToken")
    token = getAccessToken() if getAccessToken else getBridgeAccessToken()
    if not token:
        return
    client = opts.get("client")
    owns_client = client is None
    http = client or httpx.AsyncClient(timeout=opts.get("timeoutMs", 10_000) / 1000)
    try:
        await http.post(f"{baseUrl.rstrip('/')}/v1/sessions/{sessionId}/archive", json={}, headers=_headers(token, opts.get("orgUUID")))
    finally:
        if owns_client:
            await http.aclose()


async def updateBridgeSessionTitle(
    sessionId: str,
    title: str,
    opts: dict[str, Any] | None = None,
    **kwargs: Any,
) -> None:
    opts = {**(opts or {}), **kwargs}
    baseUrl = opts.get("baseUrl") or getBridgeBaseUrl()
    getAccessToken = opts.get("getAccessToken")
    token = getAccessToken() if getAccessToken else getBridgeAccessToken()
    if not token:
        return
    client = opts.get("client")
    owns_client = client is None
    http = client or httpx.AsyncClient(timeout=10.0)
    try:
        await http.patch(
            f"{baseUrl.rstrip('/')}/v1/sessions/{toCompatSessionId(sessionId)}",
            json={"title": title},
            headers=_headers(token, opts.get("orgUUID")),
        )
    except httpx.HTTPError:
        return
    finally:
        if owns_client:
            await http.aclose()
