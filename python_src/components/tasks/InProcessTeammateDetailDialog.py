from __future__ import annotations

from typing import Any

from python_src.components.tasks._shared import normalize_task, task_payload


async def InProcessTeammateDetailDialog(*args: Any, **kwargs: Any) -> Any:
    task = normalize_task(kwargs.get("task") or (args[0] if args else None), **kwargs)
    return task_payload("in_process_teammate_detail_dialog", task=task, teammate=task.get("agent") or "teammate")


__all__ = ["InProcessTeammateDetailDialog"]
