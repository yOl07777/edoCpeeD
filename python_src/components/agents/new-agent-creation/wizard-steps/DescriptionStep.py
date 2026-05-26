from __future__ import annotations

from typing import Any

from python_src.components.agents._shared import component_result


async def DescriptionStep(*args: Any, **kwargs: Any) -> Any:
    value = str(kwargs.get("description") or kwargs.get("whenToUse") or (args[0] if args else "") or "")
    return component_result("agent_wizard_description_step", field="whenToUse", value=value, complete=len(value) >= 10)


__all__ = ["DescriptionStep"]
