from __future__ import annotations

from typing import Any


async def TeammateSpinnerTree(*args: Any, **kwargs: Any) -> dict[str, Any]:
    agents = kwargs.get("agents") or kwargs.get("teammates") or (args[0] if args else []) or []
    if isinstance(agents, dict):
        agents = [agents]
    rows = [
        {"name": item.get("name", f"agent-{index}") if isinstance(item, dict) else str(item), "status": item.get("status", "working") if isinstance(item, dict) else "working"}
        for index, item in enumerate(agents, start=1)
    ]
    return {"type": "teammate_spinner_tree", "provider": "deepseek", "agents": rows}


__all__ = ["TeammateSpinnerTree"]
