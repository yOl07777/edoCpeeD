from __future__ import annotations

from typing import Any

from python_src.components.mcp._shared import mcp_payload, normalize_server


async def MCPSettings(*args: Any, **kwargs: Any) -> Any:
    config = kwargs.get("config") or (args[0] if args else {}) or {}
    servers = config.get("servers", []) if isinstance(config, dict) else []
    rows = [normalize_server(server, index) for index, server in enumerate(servers)]
    return mcp_payload("mcp_settings", servers=rows, count=len(rows), config=config)


__all__ = ["MCPSettings"]
