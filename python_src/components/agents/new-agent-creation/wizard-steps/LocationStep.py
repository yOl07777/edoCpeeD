from __future__ import annotations

from typing import Any

from python_src.components.agents._shared import component_result


async def LocationStep(*args: Any, **kwargs: Any) -> Any:
    selected = str(kwargs.get("source") or kwargs.get("location") or (args[0] if args else "projectSettings"))
    options = ["projectSettings", "userSettings", "localSettings"]
    return component_result("agent_wizard_location_step", field="source", selected=selected, options=[{"id": option, "selected": option == selected} for option in options], complete=selected in options)


__all__ = ["LocationStep"]
