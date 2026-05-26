from __future__ import annotations

from typing import Any

from ._state import stop_task


class StopTaskError(Exception):
    pass


async def stopTask(*args: Any, **kwargs: Any) -> dict[str, Any]:
    task = kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None)
    reason = str(kwargs.get("reason") or (args[1] if len(args) > 1 else "stopped"))
    stopped = stop_task(task, reason)
    if stopped is None:
        raise StopTaskError(f"Task not found: {task}")
    return {"stopped": True, "task": stopped}


__all__ = ["StopTaskError", "stopTask"]
