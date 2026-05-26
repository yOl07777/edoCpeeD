from __future__ import annotations

from typing import Any

from python_src.components.mcp._shared import mcp_payload, normalize_server


async def MCPStdioServerMenu(*args: Any, **kwargs: Any) -> Any:
    server = normalize_server(kwargs.get("server") or (args[0] if args else {}))
    command = kwargs.get("command") or ""
    server["transport"] = "stdio"
    return mcp_payload("mcp_stdio_server_menu", server=server, command=str(command), actions=["start", "stop", "restart"])


__all__ = ["MCPStdioServerMenu"]
