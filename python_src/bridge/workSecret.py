"""Work-secret helpers for bridge workers."""

from __future__ import annotations

import base64
import json
from typing import Any

import httpx


def _b64url_decode(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def decodeWorkSecret(secret: str) -> dict[str, Any]:
    try:
        parsed = json.loads(_b64url_decode(secret).decode("utf-8"))
    except Exception as exc:
        raise ValueError("Invalid work secret: not valid base64url JSON") from exc
    if not isinstance(parsed, dict) or parsed.get("version") != 1:
        version = parsed.get("version") if isinstance(parsed, dict) else "unknown"
        raise ValueError(f"Unsupported work secret version: {version}")
    token = parsed.get("session_ingress_token")
    if not isinstance(token, str) or not token:
        raise ValueError("Invalid work secret: missing or empty session_ingress_token")
    if not isinstance(parsed.get("api_base_url"), str):
        raise ValueError("Invalid work secret: missing api_base_url")
    return parsed


def buildSdkUrl(apiBaseUrl: str, sessionId: str) -> str:
    is_localhost = "localhost" in apiBaseUrl or "127.0.0.1" in apiBaseUrl
    protocol = "ws" if is_localhost else "wss"
    version = "v2" if is_localhost else "v1"
    host = apiBaseUrl.removeprefix("https://").removeprefix("http://").rstrip("/")
    return f"{protocol}://{host}/{version}/session_ingress/ws/{sessionId}"


def sameSessionId(a: str, b: str) -> bool:
    if a == b:
        return True
    a_body = a.rsplit("_", 1)[-1]
    b_body = b.rsplit("_", 1)[-1]
    return len(a_body) >= 4 and a_body == b_body


def buildCCRv2SdkUrl(apiBaseUrl: str, sessionId: str) -> str:
    return f"{apiBaseUrl.rstrip('/')}/v1/code/sessions/{sessionId}"


async def registerWorker(
    sessionUrl: str,
    accessToken: str,
    *,
    client: httpx.AsyncClient | None = None,
) -> int:
    owns_client = client is None
    http = client or httpx.AsyncClient(timeout=10.0)
    try:
        response = await http.post(
            f"{sessionUrl.rstrip('/')}/worker/register",
            json={},
            headers={
                "Authorization": f"Bearer {accessToken}",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        data = response.json()
    finally:
        if owns_client:
            await http.aclose()
    raw = data.get("worker_epoch") if isinstance(data, dict) else None
    try:
        epoch = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"registerWorker: invalid worker_epoch in response: {data}") from exc
    if epoch < 0:
        raise ValueError(f"registerWorker: invalid worker_epoch in response: {data}")
    return epoch
