from __future__ import annotations

from typing import Any

from python_src.components.agents._shared import coerce_agent, component_result
from python_src.components.agents.agentFileUtils import getNewRelativeAgentFilePath
from python_src.components.agents.validateAgent import validateAgent


async def ConfirmStep(*args: Any, **kwargs: Any) -> Any:
    agent = coerce_agent(kwargs.get("agent") or (args[0] if args else None), **kwargs)
    validation = await validateAgent(agent, kwargs.get("availableTools", []), kwargs.get("existingAgents", []))
    return component_result(
        "agent_wizard_confirm_step",
        agent=agent,
        targetPath=await getNewRelativeAgentFilePath(agent),
        validation=validation,
        complete=validation["isValid"],
    )


__all__ = ["ConfirmStep"]
