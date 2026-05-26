from __future__ import annotations

from typing import Any

from python_src.components.agents._shared import coerce_agent, component_result
from python_src.components.agents.validateAgent import validateAgent


async def CreateAgentWizard(*args: Any, **kwargs: Any) -> Any:
    agent = coerce_agent(kwargs.get("agent") or (args[0] if args else None), **kwargs)
    step = kwargs.get("step") or "type"
    validation = await validateAgent(agent, kwargs.get("availableTools", []), kwargs.get("existingAgents", []))
    return component_result(
        "create_agent_wizard",
        step=step,
        agent=agent,
        validation=validation,
        steps=["method", "type", "description", "prompt", "tools", "model", "color", "memory", "location", "confirm"],
        canFinish=validation["isValid"],
    )


__all__ = ["CreateAgentWizard"]
