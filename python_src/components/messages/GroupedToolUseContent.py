from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload


async def GroupedToolUseContent(*args: Any, **kwargs: Any) -> Any:
    tools = kwargs.get("tools") or kwargs.get("toolCalls") or (args[0] if args else []) or []
    rows = []
    for index, tool in enumerate(tools):
        if isinstance(tool, dict):
            name = tool.get("name") or tool.get("function", {}).get("name") or f"tool-{index}"
        else:
            name = str(tool)
        rows.append({"index": index, "name": str(name)})
    return message_payload("grouped_tool_use_content", tools=rows, count=len(rows))


__all__ = ["GroupedToolUseContent"]
