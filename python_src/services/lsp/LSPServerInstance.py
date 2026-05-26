"""Local LSP server instance facade."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .LSPClient import LocalLSPClient, createLSPClient


class LocalLSPServerInstance:
    def __init__(self, server: dict[str, Any], root: str | Path = ".") -> None:
        self.server = dict(server)
        self.root = Path(root).resolve()
        self.client = LocalLSPClient(self.root, self.server)
        self.running = True

    async def status(self) -> dict[str, Any]:
        return {"id": self.server.get("id"), "running": self.running, "root": str(self.root)}

    async def shutdown(self) -> dict[str, Any]:
        self.running = False
        await self.client.shutdown()
        return await self.status()


async def createLSPServerInstance(server: dict[str, Any], root: str | Path = ".") -> LocalLSPServerInstance:
    return LocalLSPServerInstance(server, root)
