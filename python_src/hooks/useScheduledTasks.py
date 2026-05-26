from __future__ import annotations

from typing import Any

from ._basic import first_mapping, listify, pick


async def useScheduledTasks(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    tasks = listify(pick(options, "tasks", default=[]))
    active = [task for task in tasks if not (isinstance(task, dict) and task.get("disabled"))]
    return {"provider": "deepseek", "tasks": tasks, "active": active, "count": len(tasks), "activeCount": len(active)}
