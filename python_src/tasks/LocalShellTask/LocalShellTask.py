from __future__ import annotations

import re
from typing import Any

from .._state import FOREGROUND, create_task, get_task, stop_task, tasks_by_kind, update_task

BACKGROUND_BASH_SUMMARY_PREFIX = "[background]"
LocalShellTask = dict[str, Any]


async def spawnShellTask(*args: Any, **kwargs: Any) -> dict[str, Any]:
    command = str(kwargs.get("command") or (args[0] if args else ""))
    task = create_task("local-shell", command=command, output=kwargs.get("output", ""), foreground=True, background=False)
    FOREGROUND.add(task["id"])
    return task


async def registerForeground(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    task = get_task(kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None))
    if task:
        update_task(task, foreground=True, background=False)
        FOREGROUND.add(task["id"])
    return task


async def unregisterForeground(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    task = get_task(kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None))
    if task:
        update_task(task, foreground=False, background=True)
        FOREGROUND.discard(task["id"])
    return task


async def backgroundExistingForegroundTask(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    task_id = next(iter(FOREGROUND), None)
    return await unregisterForeground(task_id) if task_id else None


async def backgroundAll(*args: Any, **kwargs: Any) -> dict[str, Any]:
    count = 0
    for task_id in list(FOREGROUND):
        task = get_task(task_id)
        if task:
            update_task(task, foreground=False, background=True)
            count += 1
    FOREGROUND.clear()
    return {"backgrounded": count}


async def hasForegroundTasks(*args: Any, **kwargs: Any) -> bool:
    return bool(FOREGROUND)


async def looksLikePrompt(*args: Any, **kwargs: Any) -> bool:
    text = str(kwargs.get("text") or (args[0] if args else ""))
    return bool(re.search(r"(^|\n).*[>$#]\s*$", text))


async def markTaskNotified(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    task = get_task(kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None))
    return update_task(task, notified=True) if task else None


__all__ = [
    "BACKGROUND_BASH_SUMMARY_PREFIX",
    "LocalShellTask",
    "backgroundAll",
    "backgroundExistingForegroundTask",
    "hasForegroundTasks",
    "looksLikePrompt",
    "markTaskNotified",
    "registerForeground",
    "spawnShellTask",
    "unregisterForeground",
]
