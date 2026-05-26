"""Singleton local LSP server manager."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .LSPServerManager import LocalLSPServerManager, createLSPServerManager

_MANAGER: LocalLSPServerManager | None = None
_STATUS: dict[str, Any] = {"initialized": False, "connected": False}


async def initializeLspServerManager(root: str | Path = ".", servers: list[dict[str, Any]] | None = None) -> LocalLSPServerManager:
    global _MANAGER, _STATUS
    _MANAGER = await createLSPServerManager(root, servers)
    _STATUS = await _MANAGER.status()
    return _MANAGER


async def getLspServerManager() -> LocalLSPServerManager:
    global _MANAGER
    if _MANAGER is None:
        _MANAGER = await initializeLspServerManager()
    return _MANAGER


async def getInitializationStatus() -> dict[str, Any]:
    if _MANAGER is not None:
        return await _MANAGER.status()
    return dict(_STATUS)


async def isLspConnected() -> bool:
    status = await getInitializationStatus()
    return bool(status.get("connected"))


async def waitForInitialization(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    return await getInitializationStatus()


async def shutdownLspServerManager() -> dict[str, Any]:
    global _MANAGER, _STATUS
    if _MANAGER is None:
        _STATUS = {"initialized": False, "connected": False}
        return dict(_STATUS)
    status = await _MANAGER.shutdown()
    _MANAGER = None
    _STATUS = {"initialized": False, "connected": False, "last": status}
    return dict(_STATUS)


async def reinitializeLspServerManager(root: str | Path = ".", servers: list[dict[str, Any]] | None = None) -> LocalLSPServerManager:
    await shutdownLspServerManager()
    return await initializeLspServerManager(root, servers)


async def _resetLspManagerForTesting() -> None:
    global _MANAGER, _STATUS
    _MANAGER = None
    _STATUS = {"initialized": False, "connected": False}
