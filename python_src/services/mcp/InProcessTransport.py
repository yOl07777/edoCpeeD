"""In-process linked transport pair for migrated MCP tests and shims."""

from __future__ import annotations

import asyncio
from typing import Any, Callable


class InProcessTransport:
    def __init__(self) -> None:
        self.peer: InProcessTransport | None = None
        self.closed = False
        self.onclose: Callable[[], Any] | None = None
        self.onerror: Callable[[Exception], Any] | None = None
        self.onmessage: Callable[[dict[str, Any]], Any] | None = None

    def _setPeer(self, peer: "InProcessTransport") -> None:
        self.peer = peer

    async def start(self) -> None:
        return None

    async def send(self, message: dict[str, Any]) -> None:
        if self.closed:
            raise RuntimeError("Transport is closed")
        peer = self.peer

        async def deliver() -> None:
            await asyncio.sleep(0)
            if peer and not peer.closed and peer.onmessage:
                peer.onmessage(message)

        asyncio.create_task(deliver())

    async def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        if self.onclose:
            self.onclose()
        if self.peer and not self.peer.closed:
            self.peer.closed = True
            if self.peer.onclose:
                self.peer.onclose()


def createLinkedTransportPair() -> tuple[InProcessTransport, InProcessTransport]:
    client = InProcessTransport()
    server = InProcessTransport()
    client._setPeer(server)
    server._setPeer(client)
    return client, server


__all__ = ["InProcessTransport", "createLinkedTransportPair"]
