"""Connection-state helper used by migrated MCP UI shims."""

from __future__ import annotations

from typing import Any

from .client import getMcpToolsCommandsAndResources, reconnectMcpServerImpl
from .config import getAllMcpConfigs, isMcpServerDisabled, setMcpServerEnabled


async def useManageMCPConnections(*args: Any, **kwargs: Any) -> dict[str, Any]:
    configs = kwargs.get("configs") or (args[0] if args else None)
    if configs is None:
        configs = (await getAllMcpConfigs()).get("servers", {})
    state = await getMcpToolsCommandsAndResources(configs=configs)

    async def reconnect(serverName: str) -> dict[str, Any]:
        return await reconnectMcpServerImpl(serverName, config=dict(configs or {}).get(serverName, {}))

    async def toggle(serverName: str, enabled: bool | None = None) -> dict[str, Any]:
        next_enabled = (not isMcpServerDisabled(serverName)) if enabled is None else bool(enabled)
        setMcpServerEnabled(serverName, next_enabled)
        return {"serverName": serverName, "enabled": next_enabled}

    return {
        "servers": state["clients"],
        "tools": state["tools"],
        "commands": state["commands"],
        "resources": state["resources"],
        "errors": state["errors"],
        "reconnectMcpServer": reconnect,
        "toggleMcpServer": toggle,
    }


__all__ = ["useManageMCPConnections"]
