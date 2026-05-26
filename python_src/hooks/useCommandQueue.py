from __future__ import annotations

from collections import deque
from typing import Any


_COMMAND_QUEUE: deque[str] = deque()


async def useCommandQueue(*args: Any, **kwargs: Any) -> dict[str, Any]:
    if kwargs.get("clear"):
        _COMMAND_QUEUE.clear()
    initial = kwargs.get("commands", args[0] if args else None)
    if initial:
        for command in initial:
            _COMMAND_QUEUE.append(str(command))
    if "enqueue" in kwargs:
        _COMMAND_QUEUE.append(str(kwargs["enqueue"]))
    next_command = _COMMAND_QUEUE.popleft() if kwargs.get("dequeue") and _COMMAND_QUEUE else None
    return {"provider": "deepseek", "queue": list(_COMMAND_QUEUE), "count": len(_COMMAND_QUEUE), "next": next_command}


__all__ = ["useCommandQueue"]
