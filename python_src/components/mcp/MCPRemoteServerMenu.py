from __future__ import annotations

from typing import Any

from python_src.components.mcp._shared import mcp_payload, normalize_server


async def MCPRemoteServerMenu(*args: Any, **kwargs: Any) -> Any:
    server = normalize_server(kwargs.get("server") or (args[0] if args else {}))
    url = kwargs.get("url") or kwargs.get("endpoint") or ""
    server["transport"] = "remote"
    return mcp_payload("mcp_remote_server_menu", server=server, url=str(url), actions=["connect", "reconnect", "disconnect"])


__all__ = ["MCPRemoteServerMenu"]
