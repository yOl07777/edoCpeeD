from __future__ import annotations

import secrets
import time
from typing import Any

from python_src.utils.task.diskOutput import getTaskOutputPath


TASK_ID_PREFIXES: dict[str, str] = {
    "local_bash": "b",
    "local_agent": "a",
    "remote_agent": "r",
    "in_process_teammate": "t",
    "local_workflow": "w",
    "monitor_mcp": "m",
    "dream": "d",
}
TASK_ID_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"
TERMINAL_TASK_STATUSES = {"completed", "failed", "killed"}


def isTerminalTaskStatus(status: str) -> bool:
    return status in TERMINAL_TASK_STATUSES


def generateTaskId(type: str) -> str:
    prefix = TASK_ID_PREFIXES.get(type, "x")
    return prefix + "".join(secrets.choice(TASK_ID_ALPHABET) for _ in range(8))


def createTaskStateBase(
    id: str,
    type: str,
    description: str,
    toolUseId: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    state: dict[str, Any] = {
        "id": id,
        "type": type,
        "status": "pending",
        "description": description,
        "toolUseId": toolUseId,
        "startTime": int(time.time() * 1000),
        "outputFile": getTaskOutputPath(id),
        "outputOffset": 0,
        "notified": False,
    }
    state.update(extra)
    return state
