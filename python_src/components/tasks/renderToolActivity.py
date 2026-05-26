from __future__ import annotations

from typing import Any


async def renderToolActivity(*args: Any, **kwargs: Any) -> Any:
    tools = kwargs.get("tools") or (args[0] if args else []) or []
    rows = []
    for index, tool in enumerate(tools):
        name = tool.get("name") if isinstance(tool, dict) else str(tool)
        status = tool.get("status", "running") if isinstance(tool, dict) else "running"
        rows.append({"index": index, "name": str(name), "status": str(status)})
    return {"type": "tool_activity", "provider": "deepseek", "tools": rows, "count": len(rows)}


__all__ = ["renderToolActivity"]
