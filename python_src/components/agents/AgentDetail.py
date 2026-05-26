from __future__ import annotations

from typing import Any

from python_src.components.agents._shared import coerce_agent, component_result
from python_src.components.agents.agentFileUtils import getActualRelativeAgentFilePath


async def AgentDetail(*args: Any, **kwargs: Any) -> Any:
    agent = coerce_agent(kwargs.get("agent") or (args[0] if args else None), **kwargs)
    return component_result(
        "agent_detail",
        agent=agent,
        path=await getActualRelativeAgentFilePath(agent),
        summary=f"{agent['agentType']}: {agent['whenToUse']}",
    )


__all__ = ["AgentDetail"]
