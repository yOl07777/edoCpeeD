"""Environment-less bridge initialization for Python/DeepSeek runtime."""

from __future__ import annotations

import asyncio
from typing import Any

from .codeSessionApi import fetchRemoteCredentials as fetchCodeSessionCredentials
from .replBridgeTransport import createV2ReplTransport


async def fetchRemoteCredentials(
    sessionId: str,
    baseUrl: str,
    accessToken: str,
    timeoutMs: int = 10_000,
    trustedDeviceToken: str | None = None,
    *,
    retries: int = 2,
    retryDelayMs: int = 250,
    client: Any | None = None,
) -> dict[str, Any] | None:
    """Fetch code-session bridge credentials with a small retry budget."""

    for attempt in range(max(1, retries + 1)):
        result = await fetchCodeSessionCredentials(
            sessionId,
            baseUrl,
            accessToken,
            timeoutMs,
            trustedDeviceToken,
            client=client,
        )
        if result is not None:
            return result
        if attempt < retries:
            await asyncio.sleep(retryDelayMs / 1000)
    return None


async def initEnvLessBridgeCore(options: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    """Create an env-less bridge handle from already-issued credentials.

    The original TS path talks to Claude CCR. The Python migration keeps the
    same shape but makes the transport explicit and local-testable so callers
    can use DeepSeek/OpenAI-compatible model execution above it.
    """

    opts = {**(options or {}), **kwargs}
    session_id = str(opts.get("sessionId") or opts.get("session_id") or "")
    credentials = opts.get("credentials")
    if credentials is None and opts.get("baseUrl") and opts.get("accessToken"):
        credentials = await fetchRemoteCredentials(
            session_id,
            str(opts["baseUrl"]),
            str(opts["accessToken"]),
            int(opts.get("timeoutMs") or 10_000),
            opts.get("trustedDeviceToken"),
            retries=int(opts.get("retries") or 2),
            client=opts.get("client"),
        )
    if credentials is None:
        credentials = {
            "worker_jwt": opts.get("ingressToken") or opts.get("accessToken") or "",
            "api_base_url": opts.get("apiBaseUrl") or opts.get("sessionUrl") or "memory://bridge",
            "expires_in": 0,
            "worker_epoch": int(opts.get("epoch") or 0),
        }

    session_url = str(opts.get("sessionUrl") or credentials.get("api_base_url") or "memory://bridge").rstrip("/")
    token = str(credentials.get("worker_jwt") or opts.get("ingressToken") or "")
    transport = await createV2ReplTransport(
        {
            "sessionUrl": session_url,
            "ingressToken": token,
            "sessionId": session_id,
            "epoch": credentials.get("worker_epoch"),
            "initialSequenceNum": opts.get("initialSequenceNum"),
            "outboundOnly": opts.get("outboundOnly", False),
        }
    )
    return {
        "mode": "envless",
        "sessionId": session_id,
        "sessionUrl": session_url,
        "credentials": credentials,
        "transport": transport,
        "close": transport.close,
    }
