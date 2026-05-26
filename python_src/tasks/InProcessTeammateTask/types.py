from __future__ import annotations

from typing import Any

TEAMMATE_MESSAGES_UI_CAP = 200


async def appendCappedMessage(*args: Any, **kwargs: Any) -> list[Any]:
    messages = list(kwargs.get("messages") or (args[0] if args else []))
    message = kwargs.get("message") if "message" in kwargs else (args[1] if len(args) > 1 else None)
    cap = int(kwargs.get("cap") or TEAMMATE_MESSAGES_UI_CAP)
    messages.append(message)
    return messages[-cap:]


async def isInProcessTeammateTask(*args: Any, **kwargs: Any) -> bool:
    task = kwargs.get("task") or (args[0] if args else {})
    return bool(isinstance(task, dict) and task.get("kind") == "in-process-teammate")


__all__ = ["TEAMMATE_MESSAGES_UI_CAP", "appendCappedMessage", "isInProcessTeammateTask"]
