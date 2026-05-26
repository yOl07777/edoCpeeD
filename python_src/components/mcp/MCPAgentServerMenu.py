from __future__ import annotations

from typing import Any

from python_src.components.mcp._shared import mcp_payload, normalize_server


async def MCPAgentServerMenu(*args: Any, **kwargs: Any) -> Any:
    server = normalize_server(kwargs.get("server") or (args[0] if args else {}))
    return mcp_payload("mcp_agent_server_menu", server=server, actions=["enable", "disable", "tools", "remove"])


__all__ = ["MCPAgentServerMenu"]
