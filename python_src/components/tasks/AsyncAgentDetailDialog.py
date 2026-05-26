from __future__ import annotations

from typing import Any

from python_src.components.tasks._shared import normalize_task, task_payload


async def AsyncAgentDetailDialog(*args: Any, **kwargs: Any) -> Any:
    task = normalize_task(kwargs.get("task") or (args[0] if args else None), **kwargs)
    return task_payload("async_agent_detail_dialog", task=task, tools=task["tools"])


__all__ = ["AsyncAgentDetailDialog"]
