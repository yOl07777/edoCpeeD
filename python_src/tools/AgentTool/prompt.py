"""Prompt construction for local AgentTool shims."""

from __future__ import annotations

from typing import Any

from .builtInAgents import getBuiltInAgents


async def formatAgentLine(*args: Any, **kwargs: Any) -> str:
    agent = args[0] if args else kwargs.get("agent", {})
    if not isinstance(agent, dict):
        return str(agent)
    name = agent.get("name") or agent.get("agentType") or "agent"
    agent_type = agent.get("agentType") or agent.get("type") or name
    description = agent.get("whenToUse") or agent.get("description") or ""
    return f"- {name} ({agent_type}): {description}".rstrip()


async def shouldInjectAgentListInMessages(*args: Any, **kwargs: Any) -> bool:
    if "enabled" in kwargs:
        return bool(kwargs["enabled"])
    messages = args[0] if args else kwargs.get("messages", [])
    return bool(messages is not None)


async def getPrompt(*args: Any, **kwargs: Any) -> str:
    agents = kwargs.get("agents")
    if agents is None:
        agents = await getBuiltInAgents()
    lines = [await formatAgentLine(agent) for agent in agents]
    header = kwargs.get("header", "Available local agents:")
    return "\n".join([header, *lines]).strip()


__all__ = ["formatAgentLine", "getPrompt", "shouldInjectAgentListInMessages"]
