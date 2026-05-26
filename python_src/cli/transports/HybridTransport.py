"""Hybrid transport shim: WebSocket-style reads with HTTP-style writes."""

from __future__ import annotations

from .WebSocketTransport import WebSocketTransport


class HybridTransport(WebSocketTransport):
    kind = "hybrid"
