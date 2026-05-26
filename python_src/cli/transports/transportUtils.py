"""Transport selection helpers."""

from __future__ import annotations

import os
from typing import Callable
from urllib.parse import urlparse, urlunparse

from .HybridTransport import HybridTransport
from .SSETransport import SSETransport
from .WebSocketTransport import WebSocketTransport


def _truthy(value: str | None) -> bool:
    return str(value or "").lower() in {"1", "true", "yes", "on"}


def _sse_url(url: str) -> str:
    parsed = urlparse(str(url))
    scheme = "https" if parsed.scheme == "wss" else "http" if parsed.scheme == "ws" else parsed.scheme
    path = parsed.path.rstrip("/") + "/worker/events/stream"
    return urlunparse((scheme, parsed.netloc, path, parsed.params, parsed.query, parsed.fragment))


def getTransportForUrl(
    url: str,
    headers: dict[str, str] | None = None,
    sessionId: str | None = None,
    refreshHeaders: Callable[[], dict[str, str]] | None = None,
):
    parsed = urlparse(str(url))
    if _truthy(os.getenv("CLAUDE_CODE_USE_CCR_V2")) or _truthy(os.getenv("DEEPSEEK_CODE_USE_CCR_V2")):
        return SSETransport(_sse_url(str(url)), headers or {}, sessionId, refreshHeaders)
    if parsed.scheme in {"ws", "wss"}:
        if _truthy(os.getenv("CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2")) or _truthy(os.getenv("DEEPSEEK_CODE_POST_FOR_SESSION_INGRESS_V2")):
            return HybridTransport(str(url), headers or {}, sessionId, refreshHeaders)
        return WebSocketTransport(str(url), headers or {}, sessionId, refreshHeaders)
    raise ValueError(f"Unsupported protocol: {parsed.scheme}:")
