from __future__ import annotations

from typing import Any

from python_src.components.tasks._shared import normalize_task, task_payload


async def BackgroundTasksDialog(*args: Any, **kwargs: Any) -> Any:
    tasks = kwargs.get("tasks") or (args[0] if args else []) or []
    rows = [normalize_task(task, index) for index, task in enumerate(tasks)]
    return task_payload("background_tasks_dialog", tasks=rows, count=len(rows), active=sum(1 for row in rows if not row["terminal"]))


__all__ = ["BackgroundTasksDialog"]
