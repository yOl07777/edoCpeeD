from __future__ import annotations

from typing import Any

from python_src.components.tasks._shared import normalize_task, task_payload


async def TaskStatusText(*args: Any, **kwargs: Any) -> Any:
    task = normalize_task(args[0] if args else kwargs.get("task"), **kwargs)
    return f"{task['title']}: {task['status']}"


async def ShellProgress(*args: Any, **kwargs: Any) -> Any:
    task = normalize_task(args[0] if args else kwargs.get("task"), **kwargs)
    return task_payload("shell_progress", task=task, text=await TaskStatusText(task))


__all__ = ["ShellProgress", "TaskStatusText"]
