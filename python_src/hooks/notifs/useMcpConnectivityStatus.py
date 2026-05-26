from __future__ import annotations

from typing import Any

from ._notification import first_mapping, notification, pick, truthy


async def useMcpConnectivityStatus(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    connected = truthy(pick(options, "connected", default=False))
    server = str(pick(options, "server", "name", default="MCP server"))
    return notification(
        visible=True,
        level="success" if connected else "warning",
        title="MCP connectivity",
        message=f"{server} is {'connected' if connected else 'disconnected'}.",
        connected=connected,
        server=server,
    )
