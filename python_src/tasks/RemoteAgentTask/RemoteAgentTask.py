from __future__ import annotations

import os
import re
from typing import Any, Callable

from .._state import NOTIFICATIONS, create_task, tasks_by_kind, update_task

RemoteAgentTask = dict[str, Any]
_completion_checkers: list[Callable[[dict[str, Any]], Any]] = []


async def checkRemoteAgentEligibility(*args: Any, **kwargs: Any) -> dict[str, Any]:
    enabled = str(os.getenv("DEEPCODE_REMOTE_AGENTS", "true")).lower() in {"1", "true", "yes", "on"}
    return {"eligible": enabled, "reason": None if enabled else "Remote agents disabled"}


async def registerRemoteAgentTask(*args: Any, **kwargs: Any) -> dict[str, Any]:
    task = create_task("remote-agent", remoteSessionId=kwargs.get("remoteSessionId"), url=kwargs.get("url"), background=True, foreground=False)
    return task


async def restoreRemoteAgentTasks(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    return tasks_by_kind("remote-agent")


async def registerCompletionChecker(*args: Any, **kwargs: Any) -> Callable[[], None]:
    checker = kwargs.get("checker") or (args[0] if args else None)
    if callable(checker):
        _completion_checkers.append(checker)

    def dispose() -> None:
        if checker in _completion_checkers:
            _completion_checkers.remove(checker)

    return dispose


async def getRemoteTaskSessionUrl(*args: Any, **kwargs: Any) -> str:
    session_id = str(kwargs.get("sessionId") or kwargs.get("remoteSessionId") or (args[0] if args else ""))
    base = str(kwargs.get("baseUrl") or os.getenv("DEEPCODE_REMOTE_BASE_URL") or "https://deepseek.local/remote")
    return base.rstrip("/") + (f"/{session_id}" if session_id else "")


async def formatPreconditionError(*args: Any, **kwargs: Any) -> str:
    error = kwargs.get("error") or (args[0] if args else "Remote agent precondition failed")
    return str(error)


async def extractPlanFromLog(*args: Any, **kwargs: Any) -> str | None:
    log = str(kwargs.get("log") or (args[0] if args else ""))
    match = re.search(r"<plan>(.*?)</plan>", log, re.S | re.I)
    return match.group(1).strip() if match else None


async def enqueueUltraplanFailureNotification(*args: Any, **kwargs: Any) -> dict[str, Any]:
    notification = {"type": "ultraplan_failure", "message": str(kwargs.get("message") or (args[0] if args else "Ultraplan failed"))}
    NOTIFICATIONS.append(notification)
    return notification


__all__ = [
    "RemoteAgentTask",
    "checkRemoteAgentEligibility",
    "enqueueUltraplanFailureNotification",
    "extractPlanFromLog",
    "formatPreconditionError",
    "getRemoteTaskSessionUrl",
    "registerCompletionChecker",
    "registerRemoteAgentTask",
    "restoreRemoteAgentTasks",
]
