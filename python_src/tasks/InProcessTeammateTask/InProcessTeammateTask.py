from __future__ import annotations

from typing import Any

from .._state import append_message, create_task, get_task, tasks_by_kind, update_task

InProcessTeammateTask = dict[str, Any]


async def getAllInProcessTeammateTasks(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    return tasks_by_kind("in-process-teammate")


async def getRunningTeammatesSorted(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    return sorted([t for t in tasks_by_kind("in-process-teammate") if t.get("status") == "running"], key=lambda t: t.get("createdAt", 0))


async def findTeammateTaskByAgentId(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    agent_id = str(kwargs.get("agentId") or (args[0] if args else ""))
    for task in tasks_by_kind("in-process-teammate"):
        if str(task.get("agentId")) == agent_id:
            return task
    return None


async def appendTeammateMessage(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    task = kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None)
    message = kwargs.get("message") if "message" in kwargs else (args[1] if len(args) > 1 else None)
    return append_message(task, message)


async def injectUserMessageToTeammate(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    message = kwargs.get("message") if "message" in kwargs else (args[1] if len(args) > 1 else None)
    task = await appendTeammateMessage(kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None), {"role": "user", "content": message})
    return task


async def requestTeammateShutdown(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    task = get_task(kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None))
    if task:
        update_task(task, status="stopping", shutdownRequested=True)
    return task


def create_teammate(agentId: str, **fields: Any) -> dict[str, Any]:
    return create_task("in-process-teammate", agentId=agentId, **fields)


__all__ = [
    "InProcessTeammateTask",
    "appendTeammateMessage",
    "create_teammate",
    "findTeammateTaskByAgentId",
    "getAllInProcessTeammateTasks",
    "getRunningTeammatesSorted",
    "injectUserMessageToTeammate",
    "requestTeammateShutdown",
]
