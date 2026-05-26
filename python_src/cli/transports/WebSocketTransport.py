"""In-memory WebSocket transport shim for the Python migration."""

from __future__ import annotations

from typing import Any, Callable


class WebSocketTransport:
    kind = "websocket"

    def __init__(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        sessionId: str | None = None,
        refreshHeaders: Callable[[], dict[str, str]] | None = None,
    ) -> None:
        self.url = str(url)
        self.headers = headers or {}
        self.sessionId = sessionId
        self.refreshHeaders = refreshHeaders
        self.connected = False
        self.closed = False
        self.sent: list[Any] = []
        self.on_data: Callable[[str], Any] | None = None
        self.on_close: Callable[[], Any] | None = None

    def setOnData(self, callback: Callable[[str], Any]) -> None:
        self.on_data = callback

    def setOnClose(self, callback: Callable[[], Any]) -> None:
        self.on_close = callback

    async def connect(self) -> None:
        self.connected = True

    async def write(self, message: Any) -> None:
        self.sent.append(message)

    def feed(self, data: str) -> None:
        if self.on_data:
            self.on_data(data)

    def close(self) -> None:
        self.closed = True
        self.connected = False
        if self.on_close:
            self.on_close()
