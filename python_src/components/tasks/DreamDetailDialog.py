from __future__ import annotations

from typing import Any

from python_src.components.tasks._shared import normalize_task, task_payload


async def DreamDetailDialog(*args: Any, **kwargs: Any) -> Any:
    task = normalize_task(kwargs.get("task") or (args[0] if args else None), **kwargs)
    return task_payload("dream_detail_dialog", task=task, notes=kwargs.get("notes") or [])


__all__ = ["DreamDetailDialog"]
