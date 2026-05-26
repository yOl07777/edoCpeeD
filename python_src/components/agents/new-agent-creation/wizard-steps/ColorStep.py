from __future__ import annotations

from typing import Any

from python_src.components.agents.ColorPicker import ColorPicker
from python_src.components.agents._shared import component_result


async def ColorStep(*args: Any, **kwargs: Any) -> Any:
    selected = kwargs.get("color") or kwargs.get("selected") or (args[0] if args else "blue")
    return component_result("agent_wizard_color_step", field="color", complete=bool(selected), picker=await ColorPicker(selected))


__all__ = ["ColorStep"]
