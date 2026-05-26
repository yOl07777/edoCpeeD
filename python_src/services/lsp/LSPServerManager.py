"""Local LSP server manager."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .LSPServerInstance import LocalLSPServerInstance, createLSPServerInstance
from .config import getAllLspServers


class LocalLSPServerManager:
    def __init__(self, root: str | Path = ".", servers: list[dict[str, Any]] | None = None) -> None:
        self.root = Path(root).resolve()
        self.servers = servers or []
        self.instances: dict[str, LocalLSPServerInstance] = {}
        self.initialized = False

    async def initialize(self) -> dict[str, Any]:
        if not self.servers:
            self.servers = await getAllLspServers()
        for server in self.servers:
            if server.get("enabled", True):
                instance = await createLSPServerInstance(server, self.root)
                self.instances[str(server.get("id"))] = instance
        self.initialized = True
        return await self.status()

    async def status(self) -> dict[str, Any]:
        return {
            "initialized": self.initialized,
            "connected": any(instance.running for instance in self.instances.values()),
            "servers": [await instance.status() for instance in self.instances.values()],
        }

    async def search_symbols(self, query: str, include: str = "**/*", limit: int = 100) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for instance in self.instances.values():
            for result in await instance.client.search_symbols(query, include=include, limit=limit - len(results)):
                result["server"] = instance.server.get("id")
                results.append(result)
                if len(results) >= limit:
                    return results
        return results

    async def shutdown(self) -> dict[str, Any]:
        for instance in self.instances.values():
            await instance.shutdown()
        self.initialized = False
        return await self.status()


async def createLSPServerManager(root: str | Path = ".", servers: list[dict[str, Any]] | None = None) -> LocalLSPServerManager:
    manager = LocalLSPServerManager(root, servers)
    await manager.initialize()
    return manager
