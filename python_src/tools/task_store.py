from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count
from typing import Any


_TASK_IDS = count(1)


@dataclass
class TaskRecord:
    id: str
    title: str
    description: str = ""
    status: str = "pending"
    output: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "output": list(self.output),
        }


TASKS: dict[str, TaskRecord] = {}


def create_task(title: str, *, description: str = "", status: str = "pending") -> TaskRecord:
    task_id = f"task_{next(_TASK_IDS)}"
    task = TaskRecord(id=task_id, title=title, description=description, status=status)
    TASKS[task_id] = task
    return task


def get_task(task_id: str) -> TaskRecord:
    try:
        return TASKS[task_id]
    except KeyError as exc:
        raise KeyError(f"Unknown task id: {task_id}") from exc


def list_tasks(status: str | None = None) -> list[TaskRecord]:
    tasks = list(TASKS.values())
    if status:
        tasks = [task for task in tasks if task.status == status]
    return tasks


def update_task(
    task_id: str,
    *,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
) -> TaskRecord:
    task = get_task(task_id)
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if status is not None:
        task.status = status
    return task


def append_task_output(task_id: str, content: str) -> TaskRecord:
    task = get_task(task_id)
    task.output.append(content)
    return task


def stop_task(task_id: str, *, reason: str = "") -> TaskRecord:
    task = get_task(task_id)
    task.status = "stopped"
    if reason:
        task.output.append(f"Stopped: {reason}")
    return task


def clear_tasks() -> None:
    TASKS.clear()
