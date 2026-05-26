from __future__ import annotations

from typing import Any

from python_src.components.agents._shared import coerce_agent, component_result
from python_src.components.agents.validateAgent import validateAgent


async def AgentEditor(*args: Any, **kwargs: Any) -> Any:
    agent = coerce_agent(kwargs.get("agent") or (args[0] if args else None), **kwargs)
    validation = await validateAgent(agent, kwargs.get("availableTools", []), kwargs.get("existingAgents", []))
    return component_result(
        "agent_editor",
        agent=agent,
        validation=validation,
        dirty=bool(kwargs.get("dirty", False)),
        actions=["save", "cancel", "delete"] if validation["isValid"] else ["cancel"],
    )


__all__ = ["AgentEditor"]
