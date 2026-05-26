from __future__ import annotations

from typing import Any

from python_src.components.tasks._shared import normalize_task, task_payload


async def BackgroundTask(*args: Any, **kwargs: Any) -> Any:
    task = normalize_task(args[0] if args else kwargs.get("task"), **kwargs)
    return task_payload("background_task", task=task)


__all__ = ["BackgroundTask"]
