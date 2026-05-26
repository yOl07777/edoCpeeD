"""Built-in AgentTool definitions for the Python migration."""

from __future__ import annotations

import os
from typing import Any

from ._registry import register_definition


BUILT_IN_AGENT_DEFINITIONS: list[dict[str, Any]] = [
    {
        "agentType": "general-purpose",
        "name": "General purpose",
        "description": "Handles broad research, coding, and analysis tasks.",
        "whenToUse": "Use for open-ended implementation or investigation work.",
        "source": "built-in",
        "tools": ["read", "search", "edit", "test"],
    },
    {
        "agentType": "explore",
        "name": "Explore",
        "description": "Searches the workspace and summarizes options before changes.",
        "whenToUse": "Use when the next step needs codebase discovery.",
        "source": "built-in",
        "tools": ["read", "search"],
    },
    {
        "agentType": "plan",
        "name": "Plan",
        "description": "Breaks complex work into a concrete implementation plan.",
        "whenToUse": "Use before broad or risky changes.",
        "source": "built-in",
        "tools": ["read", "search"],
    },
    {
        "agentType": "verification",
        "name": "Verification",
        "description": "Checks completed work and reports residual risk.",
        "whenToUse": "Use after implementation to validate behavior.",
        "source": "built-in",
        "tools": ["read", "test"],
    },
    {
        "agentType": "claude-code-guide",
        "name": "DeepSeek Code guide",
        "description": "Provides local migration guidance for Claude Code compatible features.",
        "whenToUse": "Use for compatibility questions during migration.",
        "source": "built-in",
        "tools": ["read"],
    },
    {
        "agentType": "statusline-setup",
        "name": "Statusline setup",
        "description": "Helps configure local statusline integrations.",
        "whenToUse": "Use when setting up shell or editor statusline display.",
        "source": "built-in",
        "tools": ["read", "edit"],
    },
]


async def areExplorePlanAgentsEnabled(*args: Any, **kwargs: Any) -> bool:
    """Return whether explore/plan agents should be exposed."""

    value = kwargs.get("enabled")
    if value is not None:
        return bool(value)
    env = os.getenv("DEEPCODE_ENABLE_EXPLORE_PLAN_AGENTS", "1").strip().lower()
    return env not in {"0", "false", "no", "off"}


async def getBuiltInAgents(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    """Register and return the built-in agent definitions."""

    include_explore_plan = await areExplorePlanAgentsEnabled(**kwargs)
    definitions: list[dict[str, Any]] = []
    for definition in BUILT_IN_AGENT_DEFINITIONS:
        if not include_explore_plan and definition["agentType"] in {"explore", "plan"}:
            continue
        definitions.append(register_definition(definition["agentType"], **definition))
    return definitions


__all__ = ["BUILT_IN_AGENT_DEFINITIONS", "areExplorePlanAgentsEnabled", "getBuiltInAgents"]
