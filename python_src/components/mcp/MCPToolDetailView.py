from __future__ import annotations

from typing import Any

from python_src.components.mcp._shared import mcp_payload, normalize_tool


async def MCPToolDetailView(*args: Any, **kwargs: Any) -> Any:
    tool = normalize_tool(kwargs.get("tool") or (args[0] if args else None))
    return mcp_payload("mcp_tool_detail_view", tool=tool, hasSchema=bool(tool["schema"]))


__all__ = ["MCPToolDetailView"]
