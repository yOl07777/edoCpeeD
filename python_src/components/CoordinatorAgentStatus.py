from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def CoordinatorTaskPanel(*args: Any, **kwargs: Any) -> Any:
    tasks = await getVisibleAgentTasks(*args, **kwargs)
    return component_payload("coordinator_task_panel", tasks=tasks, count=len(tasks), expanded=bool(option(args, kwargs, "expanded", True)))


async def getVisibleAgentTasks(*args: Any, **kwargs: Any) -> Any:
    rows = normalize_items(option(args, kwargs, "tasks", scalar_arg(args, [])), text_key="title")
    if bool(option(args, kwargs, "includeCompleted", False)):
        return rows
    return [row for row in rows if str(row.get("status", "running")) not in {"completed", "done"}]


async def useCoordinatorTaskCount(*args: Any, **kwargs: Any) -> Any:
    tasks = await getVisibleAgentTasks(*args, **kwargs)
    return component_payload("coordinator_task_count", count=len(tasks), active=sum(1 for task in tasks if str(task.get("status", "running")) == "running"))


__all__ = ["CoordinatorTaskPanel", "getVisibleAgentTasks", "useCoordinatorTaskCount"]
