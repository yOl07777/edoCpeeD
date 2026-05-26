from __future__ import annotations

from typing import Any

from python_src.components.mcp._shared import mcp_payload, normalize_server


async def MCPListPanel(*args: Any, **kwargs: Any) -> Any:
    servers = kwargs.get("servers") or (args[0] if args else []) or []
    rows = [normalize_server(server, index) for index, server in enumerate(servers)]
    return mcp_payload("mcp_list_panel", servers=rows, count=len(rows), connected=sum(1 for row in rows if row["status"] in {"enabled", "connected"}))


__all__ = ["MCPListPanel"]
