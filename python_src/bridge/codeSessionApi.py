"""Thin HTTP wrappers for CCR/code-session style APIs."""

from __future__ import annotations

from typing import Any

import httpx


def _headers(accessToken: str, trustedDeviceToken: str | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {accessToken}", "Content-Type": "application/json"}
    if trustedDeviceToken:
        headers["X-Trusted-Device-Token"] = trustedDeviceToken
    return headers


async def createCodeSession(
    baseUrl: str,
    accessToken: str,
    title: str,
    timeoutMs: int,
    tags: list[str] | None = None,
    *,
    client: httpx.AsyncClient | None = None,
) -> str | None:
    owns_client = client is None
    http = client or httpx.AsyncClient(timeout=timeoutMs / 1000)
    try:
        response = await http.post(
            f"{baseUrl.rstrip('/')}/v1/code/sessions",
            json={"title": title, "bridge": {}, **({"tags": tags} if tags else {})},
            headers=_headers(accessToken),
        )
        if response.status_code not in {200, 201}:
            return None
        data = response.json()
    except (httpx.HTTPError, ValueError):
        return None
    finally:
        if owns_client:
            await http.aclose()
    session = data.get("session") if isinstance(data, dict) else None
    session_id = session.get("id") if isinstance(session, dict) else None
    return session_id if isinstance(session_id, str) and session_id.startswith("cse_") else None


async def fetchRemoteCredentials(
    sessionId: str,
    baseUrl: str,
    accessToken: str,
    timeoutMs: int,
    trustedDeviceToken: str | None = None,
    *,
    client: httpx.AsyncClient | None = None,
) -> dict[str, Any] | None:
    owns_client = client is None
    http = client or httpx.AsyncClient(timeout=timeoutMs / 1000)
    try:
        response = await http.post(
            f"{baseUrl.rstrip('/')}/v1/code/sessions/{sessionId}/bridge",
            json={},
            headers=_headers(accessToken, trustedDeviceToken),
        )
        if response.status_code != 200:
            return None
        data = response.json()
    except (httpx.HTTPError, ValueError):
        return None
    finally:
        if owns_client:
            await http.aclose()
    if not isinstance(data, dict):
        return None
    worker_jwt = data.get("worker_jwt")
    api_base_url = data.get("api_base_url")
    expires_in = data.get("expires_in")
    raw_epoch = data.get("worker_epoch")
    try:
        worker_epoch = int(raw_epoch)
    except (TypeError, ValueError):
        return None
    if not isinstance(worker_jwt, str) or not isinstance(api_base_url, str):
        return None
    if not isinstance(expires_in, (int, float)) or worker_epoch < 0:
        return None
    return {
        "worker_jwt": worker_jwt,
        "api_base_url": api_base_url,
        "expires_in": int(expires_in),
        "worker_epoch": worker_epoch,
    }
