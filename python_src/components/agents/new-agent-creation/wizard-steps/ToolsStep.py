from __future__ import annotations

from typing import Any

from python_src.components.agents.ToolSelector import ToolSelector
from python_src.components.agents._shared import component_result


async def ToolsStep(*args: Any, **kwargs: Any) -> Any:
    tools = kwargs.get("tools") or (args[0] if args else []) or []
    selected = kwargs.get("selected") or kwargs.get("selectedTools") or []
    return component_result("agent_wizard_tools_step", field="tools", selector=await ToolSelector(tools, selected=selected), complete=True)


__all__ = ["ToolsStep"]
