from __future__ import annotations

from typing import Any

from python_src.components.mcp._shared import mcp_payload, normalize_tool


async def MCPToolListView(*args: Any, **kwargs: Any) -> Any:
    tools = kwargs.get("tools") or (args[0] if args else []) or []
    query = str(kwargs.get("query") or "").lower()
    rows = [normalize_tool(tool, index) for index, tool in enumerate(tools)]
    if query:
        rows = [tool for tool in rows if query in tool["name"].lower() or query in tool["description"].lower()]
    return mcp_payload("mcp_tool_list_view", tools=rows, count=len(rows), query=query)


__all__ = ["MCPToolListView"]
