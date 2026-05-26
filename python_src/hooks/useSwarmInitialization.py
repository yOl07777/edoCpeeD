from __future__ import annotations

from typing import Any

from ._basic import first_mapping, listify, pick


async def useSwarmInitialization(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    agents = listify(pick(options, "agents", "teammates", default=[]))
    goal = str(pick(options, "goal", default=""))
    return {
        "provider": "deepseek",
        "initialized": bool(agents),
        "agents": agents,
        "goal": goal,
        "message": f"Initialized {len(agents)} DeepSeek teammate(s)." if agents else "No teammates selected.",
    }
