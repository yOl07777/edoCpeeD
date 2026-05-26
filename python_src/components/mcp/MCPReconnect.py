from __future__ import annotations

from typing import Any

from python_src.components.mcp._shared import mcp_payload, normalize_server


async def MCPReconnect(*args: Any, **kwargs: Any) -> Any:
    server = normalize_server(kwargs.get("server") or (args[0] if args else {}))
    result = kwargs.get("result") or {}
    ok = bool(result.get("ok", kwargs.get("ok", False))) if isinstance(result, dict) else bool(result)
    return mcp_payload("mcp_reconnect", server=server, ok=ok, message="Reconnect succeeded" if ok else "Reconnect pending or failed")


__all__ = ["MCPReconnect"]
