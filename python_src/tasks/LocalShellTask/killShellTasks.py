from __future__ import annotations

from typing import Any

from .._state import stop_task, tasks_by_kind


async def killTask(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    return stop_task(kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None), str(kwargs.get("reason") or "killed"))


async def killShellTasksForAgent(*args: Any, **kwargs: Any) -> dict[str, Any]:
    agent_id = str(kwargs.get("agentId") or (args[0] if args else ""))
    killed = 0
    for task in tasks_by_kind("local-shell"):
        if not agent_id or str(task.get("agentId")) == agent_id:
            stop_task(task, "killed")
            killed += 1
    return {"killed": killed, "agentId": agent_id or None}


__all__ = ["killShellTasksForAgent", "killTask"]
