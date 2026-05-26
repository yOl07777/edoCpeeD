from __future__ import annotations

from typing import Any

from python_src.components.agents._shared import component_result


async def ToolSelector(*args: Any, **kwargs: Any) -> Any:
    selected = set(kwargs.get("selected") or [])
    tools = kwargs.get("tools") or (args[0] if args else []) or []
    rows = []
    for tool in tools:
        name = tool if isinstance(tool, str) else tool.get("name") or tool.get("id")
        rows.append({"name": str(name), "selected": "*" in selected or str(name) in selected})
    return component_result("tool_selector", tools=rows, selected=sorted(selected))


__all__ = ["ToolSelector"]
