from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def TaskListV2(*args: Any, **kwargs: Any) -> dict[str, Any]:
    tasks = normalize_items(option(args, kwargs, "tasks", scalar_arg(args, [])), text_key="title")
    active_statuses = {"active", "running", "pending", "in_progress"}
    active = [task for task in tasks if str(task.get("status", "pending")).lower() in active_statuses]
    completed = [task for task in tasks if str(task.get("status", "")).lower() in {"done", "completed", "success"}]
    return component_payload("task_list_v2", tasks=tasks, count=len(tasks), active=len(active), completed=len(completed))


__all__ = ["TaskListV2"]
