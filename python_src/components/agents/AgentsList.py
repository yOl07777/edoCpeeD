from __future__ import annotations

from typing import Any

from python_src.components.agents._shared import coerce_agent, component_result


async def AgentsList(*args: Any, **kwargs: Any) -> Any:
    agents = kwargs.get("agents") or (args[0] if args else []) or []
    rows = [coerce_agent(agent) for agent in agents]
    source = kwargs.get("source", "all")
    if source not in {"all", None}:
        rows = [agent for agent in rows if agent["source"] == source]
    return component_result("agents_list", agents=rows, count=len(rows), source=source or "all")


__all__ = ["AgentsList"]
