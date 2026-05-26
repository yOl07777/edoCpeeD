from __future__ import annotations

from typing import Any


TERMINAL_STATUSES = {"completed", "failed", "canceled", "cancelled", "done"}


def task_payload(component: str, **kwargs: Any) -> dict[str, Any]:
    payload = {"type": component, "provider": "deepseek"}
    payload.update(kwargs)
    return payload


def normalize_task(task: Any = None, index: int = 0, **kwargs: Any) -> dict[str, Any]:
    data = dict(task) if isinstance(task, dict) else {}
    if task is not None and not isinstance(task, dict):
        data["title"] = str(task)
    data.update({key: value for key, value in kwargs.items() if value is not None})
    status = str(data.get("status") or "running")
    task_id = str(data.get("id") or data.get("taskId") or f"task-{index}")
    title = str(data.get("title") or data.get("name") or task_id)
    return {
        "index": index,
        "id": task_id,
        "title": title,
        "status": status,
        "agent": data.get("agent") or data.get("assignee"),
        "progress": data.get("progress", 0),
        "terminal": status in TERMINAL_STATUSES,
        "tools": data.get("tools") or data.get("toolUses") or [],
    }

