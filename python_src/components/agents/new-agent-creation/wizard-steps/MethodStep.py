from __future__ import annotations

from typing import Any

from python_src.components.agents._shared import component_result


async def MethodStep(*args: Any, **kwargs: Any) -> Any:
    selected = str(kwargs.get("method") or (args[0] if args else "manual"))
    options = ["manual", "generate"]
    return component_result("agent_wizard_method_step", field="method", selected=selected, options=[{"id": option, "selected": option == selected} for option in options], complete=selected in options)


__all__ = ["MethodStep"]
