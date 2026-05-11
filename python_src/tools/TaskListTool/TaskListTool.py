from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.task_store import list_tasks


async def task_list(status: str | None = None) -> dict[str, Any]:
    tasks = [task.to_dict() for task in list_tasks(status=status)]
    return {"count": len(tasks), "tasks": tasks}


TaskListTool = PythonTool(
    name="task_list",
    description="List in-memory tasks for the current process.",
    parameters=object_schema(
        {"status": {"type": "string", "description": "Optional status filter."}},
    ),
    handler=task_list,
    read_only=True,
)
