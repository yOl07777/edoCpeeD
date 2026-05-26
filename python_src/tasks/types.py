from __future__ import annotations

from typing import Any


async def isBackgroundTask(*args: Any, **kwargs: Any) -> bool:
    task = kwargs.get("task") or (args[0] if args else {})
    return bool(isinstance(task, dict) and (task.get("background") or task.get("status") in {"background", "running"} and task.get("foreground") is False))


__all__ = ["isBackgroundTask"]
