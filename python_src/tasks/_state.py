"""Shared in-memory task state for migrated task shims."""

from __future__ import annotations

import time
import uuid
from typing import Any

TASKS: dict[str, dict[str, Any]] = {}
FOREGROUND: set[str] = set()
NOTIFICATIONS: list[dict[str, Any]] = []


def task_id(prefix: str = "task") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def now_ms() -> int:
    return int(time.time() * 1000)


def create_task(kind: str, **fields: Any) -> dict[str, Any]:
    tid = str(fields.pop("id", "") or fields.pop("taskId", "") or task_id(kind))
    task = {
        "id": tid,
        "taskId": tid,
        "kind": kind,
        "type": kind,
        "status": fields.pop("status", "running"),
        "createdAt": now_ms(),
        "updatedAt": now_ms(),
        "messages": [],
        "pendingMessages": [],
        "progress": {},
        "notified": False,
        **fields,
    }
    TASKS[tid] = task
    return task


def get_task(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        tid = value.get("taskId") or value.get("id")
        return TASKS.get(str(tid)) or value
    return TASKS.get(str(value))


def update_task(value: Any, **fields: Any) -> dict[str, Any] | None:
    task = get_task(value)
    if task is None:
        return None
    task.update(fields)
    task["updatedAt"] = now_ms()
    if task.get("id"):
        TASKS[str(task["id"])] = task
    return task


def append_message(task_value: Any, message: Any) -> dict[str, Any] | None:
    task = get_task(task_value)
    if task is None:
        return None
    task.setdefault("messages", []).append(message)
    task["updatedAt"] = now_ms()
    return task


def stop_task(value: Any, reason: str = "stopped") -> dict[str, Any] | None:
    task = update_task(value, status="stopped", stopReason=reason)
    if task:
        FOREGROUND.discard(str(task.get("id") or task.get("taskId")))
    return task


def tasks_by_kind(kind: str) -> list[dict[str, Any]]:
    return [task for task in TASKS.values() if task.get("kind") == kind or task.get("type") == kind]


def reset_tasks() -> None:
    TASKS.clear()
    FOREGROUND.clear()
    NOTIFICATIONS.clear()


__all__ = [
    "FOREGROUND",
    "NOTIFICATIONS",
    "TASKS",
    "append_message",
    "create_task",
    "get_task",
    "now_ms",
    "reset_tasks",
    "stop_task",
    "task_id",
    "tasks_by_kind",
    "update_task",
]
