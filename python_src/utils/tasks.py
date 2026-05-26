"""Local task-list utilities for the Python migration."""

from __future__ import annotations

import json
import os
import re
import uuid
from pathlib import Path
from typing import Any, Callable

DEFAULT_TASKS_MODE_TASK_LIST_ID = "default"
TASK_STATUSES = ["pending", "in_progress", "blocked", "completed", "stopped"]
TaskStatusSchema = {"type": "string", "enum": TASK_STATUSES}
TaskSchema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "status": TaskStatusSchema,
        "assignee": {"type": "string"},
        "description": {"type": "string"},
    },
    "required": ["id", "title", "status"],
    "additionalProperties": True,
}

_TASKS: dict[str, dict[str, Any]] = {}
_LEADER_TEAM_NAME: str | None = None
_SUBSCRIBERS: list[Callable[[list[dict[str, Any]]], Any]] = []


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


def _base_dir(value: str | Path | None = None) -> Path:
    root = value or os.getenv("DEEPCODE_TASKS_DIR") or ".deepseek_tasks"
    return Path(root).expanduser()


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _snapshot() -> list[dict[str, Any]]:
    return [dict(task) for task in _TASKS.values()]


def _notify() -> None:
    snapshot = _snapshot()
    for callback in list(_SUBSCRIBERS):
        callback(snapshot)


async def sanitizePathComponent(*args: Any, **kwargs: Any) -> str:
    value = str(args[0] if args else kwargs.get("value") or "")
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip(".-")
    return slug or "task"


async def getTaskListId(*args: Any, **kwargs: Any) -> str:
    return str(args[0] if args else kwargs.get("task_list_id") or kwargs.get("taskListId") or DEFAULT_TASKS_MODE_TASK_LIST_ID)


async def getTasksDir(*args: Any, **kwargs: Any) -> str:
    return str(_base_dir(args[0] if args else kwargs.get("path") or kwargs.get("tasks_dir") or kwargs.get("tasksDir")))


async def ensureTasksDir(*args: Any, **kwargs: Any) -> str:
    path = _base_dir(args[0] if args else kwargs.get("path") or kwargs.get("tasks_dir") or kwargs.get("tasksDir"))
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


async def getTaskPath(*args: Any, **kwargs: Any) -> str:
    task_id = str(args[0] if args else kwargs.get("task_id") or kwargs.get("taskId") or "")
    tasks_dir = _base_dir(kwargs.get("tasks_dir") or kwargs.get("tasksDir") or kwargs.get("path"))
    safe = await sanitizePathComponent(task_id or "tasks")
    return str(tasks_dir / f"{safe}.json")


def _normalize_task(data: dict[str, Any]) -> dict[str, Any]:
    task = {key: value for key, value in data.items() if key not in {"tasks_dir", "tasksDir", "path", "persist"}}
    task.setdefault("id", task.get("taskId") or uuid.uuid4().hex)
    task.setdefault("taskId", task["id"])
    task.setdefault("title", task.get("content") or "Untitled task")
    task.setdefault("description", "")
    task.setdefault("status", "pending")
    task.setdefault("assignee", None)
    task.setdefault("output", [])
    return task


async def createTask(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    persist = bool(data.get("persist") or data.get("tasks_dir") or data.get("tasksDir"))
    tasks_dir = data.get("tasks_dir") or data.get("tasksDir") or data.get("path")
    task = _normalize_task(data)
    _TASKS[str(task["id"])] = task
    if persist:
        _save(Path(await getTaskPath(task["id"], tasks_dir=tasks_dir)), task)
    _notify()
    return dict(task)


async def getTask(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    task_id = str(args[0] if args else kwargs.get("task_id") or kwargs.get("taskId") or kwargs.get("id") or "")
    if task_id in _TASKS:
        return dict(_TASKS[task_id])
    path = Path(await getTaskPath(task_id, **kwargs))
    return _normalize_task(_load(path)) if path.exists() else None


async def listTasks(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    status = kwargs.get("status")
    assignee = kwargs.get("assignee")
    tasks = _snapshot()
    if status:
        tasks = [task for task in tasks if task.get("status") == status]
    if assignee:
        tasks = [task for task in tasks if task.get("assignee") == assignee]
    return tasks


async def updateTask(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    task_id = str(data.pop("task_id", None) or data.pop("taskId", None) or data.pop("id", None) or "")
    current = _TASKS.get(task_id) or (await getTask(task_id, **data))
    if current is None:
        raise KeyError(f"Unknown task id: {task_id}")
    for key, value in data.items():
        if value is not None and key not in {"tasks_dir", "tasksDir", "path", "persist"}:
            current[key] = value
    current["taskId"] = current.get("id", task_id)
    _TASKS[task_id] = current
    if data.get("persist") or data.get("tasks_dir") or data.get("tasksDir"):
        _save(Path(await getTaskPath(task_id, **data)), current)
    _notify()
    return dict(current)


async def deleteTask(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    task_id = str(args[0] if args else kwargs.get("task_id") or kwargs.get("taskId") or kwargs.get("id") or "")
    removed = _TASKS.pop(task_id, None)
    path = Path(await getTaskPath(task_id, **kwargs))
    if path.exists():
        path.unlink()
    _notify()
    return dict(removed) if removed else None


async def resetTaskList(*args: Any, **kwargs: Any) -> dict[str, int]:
    count = len(_TASKS)
    _TASKS.clear()
    _notify()
    return {"cleared": count}


async def claimTask(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    assignee = data.get("assignee") or data.get("teammate") or data.get("agent") or "agent"
    return await updateTask({**data, "assignee": assignee, "status": data.get("status", "in_progress")})


async def blockTask(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    reason = data.get("reason", "")
    task = await updateTask({**data, "status": "blocked"})
    if reason:
        task["blocked_reason"] = reason
        _TASKS[str(task["id"])] = task
    return dict(task)


async def unassignTeammateTasks(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    teammate = str(args[0] if args else kwargs.get("teammate") or kwargs.get("assignee") or "")
    changed = []
    for task in _TASKS.values():
        if task.get("assignee") == teammate:
            task["assignee"] = None
            changed.append(dict(task))
    if changed:
        _notify()
    return changed


async def getAgentStatuses(*args: Any, **kwargs: Any) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for task in _TASKS.values():
        assignee = task.get("assignee")
        if assignee:
            statuses[str(assignee)] = str(task.get("status", "pending"))
    return statuses


async def notifyTasksUpdated(*args: Any, **kwargs: Any) -> dict[str, Any]:
    _notify()
    return {"count": len(_TASKS), "tasks": _snapshot()}


def onTasksUpdated(callback: Callable[[list[dict[str, Any]]], Any] | None = None) -> Callable[[], None]:
    if callback is None:
        return lambda: None
    _SUBSCRIBERS.append(callback)

    def unsubscribe() -> None:
        if callback in _SUBSCRIBERS:
            _SUBSCRIBERS.remove(callback)

    return unsubscribe


async def setLeaderTeamName(*args: Any, **kwargs: Any) -> str:
    global _LEADER_TEAM_NAME
    _LEADER_TEAM_NAME = str(args[0] if args else kwargs.get("name") or kwargs.get("team") or "")
    return _LEADER_TEAM_NAME


async def clearLeaderTeamName(*args: Any, **kwargs: Any) -> None:
    global _LEADER_TEAM_NAME
    _LEADER_TEAM_NAME = None
    return None


async def isTodoV2Enabled(*args: Any, **kwargs: Any) -> bool:
    value = kwargs.get("enabled")
    if value is not None:
        return bool(value)
    return os.getenv("DEEPCODE_TODO_V2", "").lower() in {"1", "true", "yes", "on"}


__all__ = [
    "DEFAULT_TASKS_MODE_TASK_LIST_ID",
    "TASK_STATUSES",
    "TaskSchema",
    "TaskStatusSchema",
    "blockTask",
    "claimTask",
    "clearLeaderTeamName",
    "createTask",
    "deleteTask",
    "ensureTasksDir",
    "getAgentStatuses",
    "getTask",
    "getTaskListId",
    "getTaskPath",
    "getTasksDir",
    "isTodoV2Enabled",
    "listTasks",
    "notifyTasksUpdated",
    "onTasksUpdated",
    "resetTaskList",
    "sanitizePathComponent",
    "setLeaderTeamName",
    "unassignTeammateTasks",
    "updateTask",
]
