"""Local `/tasks` command shim."""

from __future__ import annotations

from typing import Any

from python_src.tools.task_store import list_tasks


def getTaskSummary(status: str | None = None) -> dict[str, Any]:
    tasks = [task.to_dict() for task in list_tasks(status)]
    return {"type": "tasks", "count": len(tasks), "tasks": tasks}


def formatTaskSummary(summary: dict[str, Any]) -> str:
    if summary["count"] == 0:
        return "No background tasks."
    lines = ["Background tasks:"]
    for task in summary["tasks"]:
        lines.append(f"- {task['id']} [{task['status']}] {task['title']}")
    return "\n".join(lines)


async def call(onDone: Any = None, _context: Any = None, args: str = "") -> dict[str, Any] | None:
    status = (args or "").strip() or None
    summary = getTaskSummary(status)
    message = formatTaskSummary(summary)
    if callable(onDone):
        try:
            onDone(message, {"display": "system"})
        except TypeError:
            onDone(message)
        return None
    return {"type": "text", "value": message, "tasks": summary}
