from __future__ import annotations

from typing import Any


async def startMCPServer(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    return {
        "type": "mcp_server",
        "provider": "deepseek",
        "status": "planned" if kwargs.get("dryRun", True) else "ready",
        "transport": kwargs.get("transport", "stdio"),
        "servers": list(kwargs.get("servers", []) or []),
        "dryRun": bool(kwargs.get("dryRun", True)),
    }


__all__ = ["startMCPServer"]
