from __future__ import annotations

from typing import Any

AGENT_SOURCE_GROUPS = ["built-in", "plugin", "userSettings", "projectSettings", "policySettings", "local"]


async def compareAgentsByName(*args: Any, **kwargs: Any) -> int:
    left = kwargs.get("left") or (args[0] if args else {})
    right = kwargs.get("right") or (args[1] if len(args) > 1 else {})
    lname = str(left.get("agentType") or left.get("name") or "") if isinstance(left, dict) else str(left)
    rname = str(right.get("agentType") or right.get("name") or "") if isinstance(right, dict) else str(right)
    return (lname > rname) - (lname < rname)


async def getOverrideSourceLabel(*args: Any, **kwargs: Any) -> str:
    source = str(kwargs.get("source") or (args[0] if args else "local"))
    return {
        "built-in": "Built in",
        "plugin": "Plugin",
        "userSettings": "User",
        "projectSettings": "Project",
        "policySettings": "Managed",
        "local": "Local",
    }.get(source, source)


async def resolveAgentModelDisplay(*args: Any, **kwargs: Any) -> str:
    agent = kwargs.get("agent") or (args[0] if args else {})
    model = agent.get("model") if isinstance(agent, dict) else None
    return str(model or "inherit")


async def resolveAgentOverrides(*args: Any, **kwargs: Any) -> dict[str, Any]:
    agent = dict(kwargs.get("agent") or (args[0] if args and isinstance(args[0], dict) else {}))
    return {
        "model": agent.get("model"),
        "tools": agent.get("tools", []),
        "permissionMode": agent.get("permissionMode"),
        "sourceLabel": await getOverrideSourceLabel(agent.get("source", "local")),
    }


__all__ = ["AGENT_SOURCE_GROUPS", "compareAgentsByName", "getOverrideSourceLabel", "resolveAgentModelDisplay", "resolveAgentOverrides"]
