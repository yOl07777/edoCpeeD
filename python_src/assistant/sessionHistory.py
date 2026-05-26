"""Session history helpers for the Python runtime.

The original TypeScript module reads historical SDK events from Claude's CCR
session API.  The Python migration keeps the same pagination contract but makes
the transport injectable so tests and DeepSeek-native deployments can provide a
local or proxy endpoint without pulling in Anthropic-specific clients.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import httpx

HISTORY_PAGE_SIZE = 100


@dataclass(slots=True)
class HistoryPage:
    events: list[dict[str, Any]]
    firstId: str | None
    hasMore: bool


@dataclass(slots=True)
class HistoryAuthCtx:
    baseUrl: str
    headers: dict[str, str]
    client: httpx.AsyncClient | None = None


async def createHistoryAuthCtx(
    sessionId: str,
    *,
    base_url: str | None = None,
    access_token: str | None = None,
    org_uuid: str | None = None,
    headers: Mapping[str, str] | None = None,
    client: httpx.AsyncClient | None = None,
) -> HistoryAuthCtx:
    """Prepare reusable auth context for session-event pagination.

    `base_url` defaults to DeepSeek-compatible local/proxy configuration via
    environment in higher layers.  Callers that still talk to a remote session
    service should pass the concrete API root explicitly.
    """

    root = (base_url or "https://api.deepseek.com/v1").rstrip("/")
    merged_headers: dict[str, str] = dict(headers or {})
    if access_token:
        merged_headers.setdefault("authorization", f"Bearer {access_token}")
    if org_uuid:
        merged_headers.setdefault("x-organization-uuid", org_uuid)
    return HistoryAuthCtx(
        baseUrl=f"{root}/sessions/{sessionId}/events",
        headers=merged_headers,
        client=client,
    )


async def _fetch_page(
    ctx: HistoryAuthCtx,
    params: Mapping[str, str | int | bool],
    _label: str,
) -> HistoryPage | None:
    owns_client = ctx.client is None
    client = ctx.client or httpx.AsyncClient(timeout=15.0)
    try:
        resp = await client.get(ctx.baseUrl, headers=ctx.headers, params=params)
    except httpx.HTTPError:
        return None
    finally:
        if owns_client:
            await client.aclose()

    if resp.status_code != 200:
        return None
    try:
        data = resp.json()
    except ValueError:
        return None

    events = data.get("data")
    return HistoryPage(
        events=events if isinstance(events, list) else [],
        firstId=data.get("first_id"),
        hasMore=bool(data.get("has_more")),
    )


async def fetchLatestEvents(
    ctx: HistoryAuthCtx,
    limit: int = HISTORY_PAGE_SIZE,
) -> HistoryPage | None:
    return await _fetch_page(ctx, {"limit": limit, "anchor_to_latest": True}, "fetchLatestEvents")


async def fetchOlderEvents(
    ctx: HistoryAuthCtx,
    beforeId: str,
    limit: int = HISTORY_PAGE_SIZE,
) -> HistoryPage | None:
    return await _fetch_page(ctx, {"limit": limit, "before_id": beforeId}, "fetchOlderEvents")
