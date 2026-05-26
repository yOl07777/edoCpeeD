from __future__ import annotations

from typing import Any, Callable

from .._state import FOREGROUND, NOTIFICATIONS, append_message, create_task, get_task, stop_task, tasks_by_kind, update_task

LocalAgentTask = dict[str, Any]


async def registerAsyncAgent(*args: Any, **kwargs: Any) -> dict[str, Any]:
    agent_id = str(kwargs.get("agentId") or kwargs.get("agentName") or (args[0] if args else "agent"))
    return create_task("local-agent", agentId=agent_id, agentName=kwargs.get("agentName", agent_id), background=True, foreground=False)


async def registerAgentForeground(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    task = get_task(kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None))
    if task:
        update_task(task, foreground=True, background=False)
        FOREGROUND.add(task["id"])
    return task


async def unregisterAgentForeground(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    task = get_task(kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None))
    if task:
        update_task(task, foreground=False, background=True)
        FOREGROUND.discard(task["id"])
    return task


async def backgroundAgentTask(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    return await unregisterAgentForeground(*args, **kwargs)


async def completeAgentTask(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    task = get_task(kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None))
    if task:
        update_task(task, status="completed", result=kwargs.get("result"))
        FOREGROUND.discard(task["id"])
    return task


async def failAgentTask(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    task = get_task(kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None))
    error = kwargs.get("error") or (args[1] if len(args) > 1 else "failed")
    if task:
        update_task(task, status="failed", error=str(error))
        FOREGROUND.discard(task["id"])
    return task


async def killAsyncAgent(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    return stop_task(kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None), str(kwargs.get("reason") or "killed"))


async def killAllRunningAgentTasks(*args: Any, **kwargs: Any) -> dict[str, Any]:
    killed = 0
    for task in tasks_by_kind("local-agent"):
        if task.get("status") == "running":
            stop_task(task, "killed")
            killed += 1
    return {"killed": killed}


async def isLocalAgentTask(*args: Any, **kwargs: Any) -> bool:
    task = kwargs.get("task") or (args[0] if args else {})
    return bool(isinstance(task, dict) and task.get("kind") == "local-agent")


async def isPanelAgentTask(*args: Any, **kwargs: Any) -> bool:
    task = kwargs.get("task") or (args[0] if args else {})
    return bool(isinstance(task, dict) and task.get("panel") is True)


async def appendMessageToLocalAgent(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    return append_message(kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None), kwargs.get("message") if "message" in kwargs else (args[1] if len(args) > 1 else None))


async def queuePendingMessage(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    task = get_task(kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None))
    message = kwargs.get("message") if "message" in kwargs else (args[1] if len(args) > 1 else None)
    if task:
        task.setdefault("pendingMessages", []).append(message)
    return task


async def drainPendingMessages(*args: Any, **kwargs: Any) -> list[Any]:
    task = get_task(kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None))
    if not task:
        return []
    pending = list(task.get("pendingMessages") or [])
    task["pendingMessages"] = []
    return pending


async def enqueueAgentNotification(*args: Any, **kwargs: Any) -> dict[str, Any]:
    notification = {"taskId": kwargs.get("taskId") or (args[0] if args else None), "message": kwargs.get("message") or (args[1] if len(args) > 1 else "")}
    NOTIFICATIONS.append(notification)
    return notification


async def markAgentsNotified(*args: Any, **kwargs: Any) -> dict[str, Any]:
    count = 0
    for task in tasks_by_kind("local-agent"):
        task["notified"] = True
        count += 1
    return {"count": count}


async def updateAgentProgress(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    task = get_task(kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None))
    progress = kwargs.get("progress") if "progress" in kwargs else (args[1] if len(args) > 1 else {})
    if task:
        task["progress"] = {**dict(task.get("progress") or {}), **(progress if isinstance(progress, dict) else {"message": str(progress)})}
    return task


async def getProgressUpdate(*args: Any, **kwargs: Any) -> dict[str, Any]:
    task = get_task(kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None))
    return dict(task.get("progress") or {}) if task else {}


async def getTokenCountFromTracker(*args: Any, **kwargs: Any) -> int:
    tracker = kwargs.get("tracker") or (args[0] if args else {})
    if isinstance(tracker, dict):
        return int(tracker.get("tokens") or tracker.get("tokenCount") or 0)
    return 0


async def createProgressTracker(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"tokens": 0, "messages": 0, "startedAt": kwargs.get("startedAt")}


async def updateProgressFromMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    tracker = kwargs.get("tracker") or (args[0] if args else {})
    message = kwargs.get("message") if "message" in kwargs else (args[1] if len(args) > 1 else "")
    if isinstance(tracker, dict):
        tracker["messages"] = int(tracker.get("messages") or 0) + 1
        tracker["tokens"] = int(tracker.get("tokens") or 0) + max(1, len(str(message)) // 4)
    return tracker


async def createActivityDescriptionResolver(*args: Any, **kwargs: Any) -> Callable[[Any], str]:
    prefix = str(kwargs.get("prefix") or (args[0] if args else "Working"))
    return lambda activity=None: f"{prefix}: {activity or 'running'}"


async def updateAgentSummary(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    task = get_task(kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None))
    summary = kwargs.get("summary") if "summary" in kwargs else (args[1] if len(args) > 1 else "")
    return update_task(task, summary=summary) if task else None


__all__ = [name for name in globals() if not name.startswith("_")]
