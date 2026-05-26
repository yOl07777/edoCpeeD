from __future__ import annotations

from typing import Any

from ._registry import AGENT_COLORS_STATE, normalize_agent_type

AGENT_COLORS = ["blue", "green", "yellow", "red", "magenta", "cyan", "gray"]
AGENT_COLOR_TO_THEME_COLOR = {name: name for name in AGENT_COLORS}


async def getAgentColor(*args: Any, **kwargs: Any) -> str:
    agent_type = normalize_agent_type(str(kwargs.get("agentType") or kwargs.get("agent") or (args[0] if args else "agent")))
    return AGENT_COLORS_STATE.get(agent_type, AGENT_COLORS[hash(agent_type) % len(AGENT_COLORS)])


async def setAgentColor(*args: Any, **kwargs: Any) -> str:
    agent_type = normalize_agent_type(str(kwargs.get("agentType") or kwargs.get("agent") or (args[0] if args else "agent")))
    color = str(kwargs.get("color") or (args[1] if len(args) > 1 else "blue"))
    if color not in AGENT_COLORS:
        color = "blue"
    AGENT_COLORS_STATE[agent_type] = color
    return color


__all__ = ["AGENT_COLORS", "AGENT_COLOR_TO_THEME_COLOR", "getAgentColor", "setAgentColor"]
