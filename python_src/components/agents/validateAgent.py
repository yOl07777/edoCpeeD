from __future__ import annotations

import re
from typing import Any

from python_src.components.agents._shared import coerce_agent
from python_src.components.agents.utils import getAgentSourceDisplayName


async def validateAgent(*args: Any, **kwargs: Any) -> Any:
    agent = coerce_agent(args[0] if args else kwargs.get("agent"), **kwargs)
    available_tools = kwargs.get("availableTools") or (args[1] if len(args) > 1 else [])
    existing_agents = kwargs.get("existingAgents") or (args[2] if len(args) > 2 else [])
    errors: list[str] = []
    warnings: list[str] = []

    type_error = await validateAgentType(agent["agentType"])
    if type_error:
        errors.append(type_error)

    for existing in existing_agents or []:
        existing_agent = coerce_agent(existing)
        if existing_agent["agentType"] == agent["agentType"] and existing_agent["source"] != agent["source"]:
            source = await getAgentSourceDisplayName(existing_agent["source"])
            errors.append(f'Agent type "{agent["agentType"]}" already exists in {source}')

    if not agent["whenToUse"]:
        errors.append("Description (description) is required")
    elif len(agent["whenToUse"]) < 10:
        warnings.append("Description should be more descriptive (at least 10 characters)")
    elif len(agent["whenToUse"]) > 5000:
        warnings.append("Description is very long (over 5000 characters)")

    tools = agent["tools"]
    if tools is None:
        warnings.append("Agent has access to all tools")
    elif not isinstance(tools, list):
        errors.append("Tools must be an array")
    elif len(tools) == 0:
        warnings.append("No tools selected - agent will have very limited capabilities")
    else:
        available_names = _tool_names(available_tools)
        if available_names:
            invalid = [tool for tool in tools if tool != "*" and str(tool) not in available_names]
            if invalid:
                errors.append(f"Invalid tools: {', '.join(str(tool) for tool in invalid)}")

    if not agent["systemPrompt"]:
        errors.append("System prompt is required")
    elif len(agent["systemPrompt"]) < 20:
        errors.append("System prompt is too short (minimum 20 characters)")
    elif len(agent["systemPrompt"]) > 10000:
        warnings.append("System prompt is very long (over 10,000 characters)")

    return {"provider": "deepseek", "isValid": not errors, "errors": errors, "warnings": warnings}

async def validateAgentType(*args: Any, **kwargs: Any) -> Any:
    agent_type = str(kwargs.get("agentType") or (args[0] if args else "") or "")
    if not agent_type:
        return "Agent type is required"
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]$", agent_type):
        return "Agent type must start and end with alphanumeric characters and contain only letters, numbers, and hyphens"
    if len(agent_type) < 3:
        return "Agent type must be at least 3 characters long"
    if len(agent_type) > 50:
        return "Agent type must be less than 50 characters"
    return None


def _tool_names(tools: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(tools, dict):
        tools = tools.values()
    for tool in tools or []:
        if isinstance(tool, str):
            names.add(tool)
        elif isinstance(tool, dict):
            name = tool.get("name") or tool.get("toolName") or tool.get("id")
            if name:
                names.add(str(name))
    return names


__all__ = ["validateAgent", "validateAgentType"]
