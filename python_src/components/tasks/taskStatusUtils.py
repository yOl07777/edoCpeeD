from __future__ import annotations

from typing import Any

from python_src.components.tasks._shared import TERMINAL_STATUSES, normalize_task


STATUS_COLORS = {
    "running": "blue",
    "queued": "gray",
    "completed": "green",
    "done": "green",
    "failed": "red",
    "canceled": "yellow",
    "cancelled": "yellow",
}

STATUS_ICONS = {
    "running": "..",
    "queued": "--",
    "completed": "OK",
    "done": "OK",
    "failed": "!!",
    "canceled": "x",
    "cancelled": "x",
}


async def isTerminalStatus(*args: Any, **kwargs: Any) -> Any:
    status = str(kwargs.get("status") or (args[0] if args else "") or "")
    return status in TERMINAL_STATUSES


async def getTaskStatusColor(*args: Any, **kwargs: Any) -> Any:
    status = str(kwargs.get("status") or (args[0] if args else "running"))
    return STATUS_COLORS.get(status, "gray")


async def getTaskStatusIcon(*args: Any, **kwargs: Any) -> Any:
    status = str(kwargs.get("status") or (args[0] if args else "running"))
    return STATUS_ICONS.get(status, "?")


async def describeTeammateActivity(*args: Any, **kwargs: Any) -> Any:
    task = normalize_task(args[0] if args else kwargs.get("task"), **kwargs)
    agent = task.get("agent") or "teammate"
    return f"{agent} is {task['status']} on {task['title']}"


async def shouldHideTasksFooter(*args: Any, **kwargs: Any) -> Any:
    tasks = kwargs.get("tasks") or (args[0] if args else []) or []
    return not tasks or all(normalize_task(task)["terminal"] for task in tasks)


__all__ = [
    "describeTeammateActivity",
    "getTaskStatusColor",
    "getTaskStatusIcon",
    "isTerminalStatus",
    "shouldHideTasksFooter",
]
