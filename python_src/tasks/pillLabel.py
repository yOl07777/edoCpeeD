from __future__ import annotations

from typing import Any


async def getPillLabel(*args: Any, **kwargs: Any) -> str:
    task = kwargs.get("task") or (args[0] if args else {})
    if not isinstance(task, dict):
        return str(task)
    name = task.get("name") or task.get("title") or task.get("agentName") or task.get("kind") or task.get("type") or "task"
    status = task.get("status") or "running"
    return f"{name}: {status}"


async def pillNeedsCta(*args: Any, **kwargs: Any) -> bool:
    task = kwargs.get("task") or (args[0] if args else {})
    return bool(isinstance(task, dict) and task.get("status") in {"completed", "failed", "stopped"} and not task.get("notified"))


__all__ = ["getPillLabel", "pillNeedsCta"]
