from __future__ import annotations

from typing import Any

from python_src.components.agents._shared import component_result
from python_src.components.agents.validateAgent import validateAgentType


async def TypeStep(*args: Any, **kwargs: Any) -> Any:
    value = str(kwargs.get("agentType") or kwargs.get("identifier") or (args[0] if args else "") or "")
    error = await validateAgentType(value)
    return component_result("agent_wizard_type_step", field="agentType", value=value, error=error, complete=error is None)


__all__ = ["TypeStep"]
