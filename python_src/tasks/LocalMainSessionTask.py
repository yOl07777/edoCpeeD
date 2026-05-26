from __future__ import annotations

from typing import Any

from ._state import FOREGROUND, create_task, get_task, update_task


async def registerMainSessionTask(*args: Any, **kwargs: Any) -> dict[str, Any]:
    task = create_task("main-session", name=kwargs.get("name", "Main session"), foreground=True, background=False)
    FOREGROUND.add(task["id"])
    return task


async def isMainSessionTask(*args: Any, **kwargs: Any) -> bool:
    task = kwargs.get("task") or (args[0] if args else {})
    return bool(isinstance(task, dict) and task.get("kind") == "main-session")


async def foregroundMainSessionTask(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    task = get_task(kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None))
    if task:
        update_task(task, foreground=True, background=False, status="running")
        FOREGROUND.add(task["id"])
    return task


async def startBackgroundSession(*args: Any, **kwargs: Any) -> dict[str, Any]:
    task = create_task("main-session", name=kwargs.get("name", "Background session"), foreground=False, background=True, status="background")
    return task


async def completeMainSessionTask(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    task = get_task(kwargs.get("task") or kwargs.get("taskId") or (args[0] if args else None))
    if task:
        update_task(task, status="completed", result=kwargs.get("result"))
        FOREGROUND.discard(task["id"])
    return task


__all__ = [
    "completeMainSessionTask",
    "foregroundMainSessionTask",
    "isMainSessionTask",
    "registerMainSessionTask",
    "startBackgroundSession",
]
