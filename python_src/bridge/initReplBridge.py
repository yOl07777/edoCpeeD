"""Entry point for creating a Python REPL bridge handle."""

from __future__ import annotations

from typing import Any

from .bridgeEnabled import isEnvLessBridgeEnabled
from .remoteBridgeCore import initEnvLessBridgeCore
from .replBridge import initBridgeCore


async def initReplBridge(options: dict[str, Any] | None = None, **kwargs: Any) -> Any:
    opts = {**(options or {}), **kwargs}
    if opts.get("envless") is True or (opts.get("envless") is None and isEnvLessBridgeEnabled()):
        return await initEnvLessBridgeCore(opts)
    return await initBridgeCore(opts)
