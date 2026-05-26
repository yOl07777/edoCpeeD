from __future__ import annotations

from typing import Any

from python_src.components.tasks._shared import normalize_task, task_payload
from python_src.components.tasks.taskStatusUtils import getTaskStatusColor, getTaskStatusIcon


async def BackgroundTaskStatus(*args: Any, **kwargs: Any) -> Any:
    task = normalize_task(args[0] if args else kwargs.get("task"), **kwargs)
    return task_payload("background_task_status", task=task, color=await getTaskStatusColor(task["status"]), icon=await getTaskStatusIcon(task["status"]))


__all__ = ["BackgroundTaskStatus"]
