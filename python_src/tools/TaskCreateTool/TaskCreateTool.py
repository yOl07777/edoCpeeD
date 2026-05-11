from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.task_store import create_task


async def task_create(
    title: str,
    *,
    description: str = "",
    status: str = "pending",
) -> dict[str, Any]:
    return create_task(title, description=description, status=status).to_dict()


TaskCreateTool = PythonTool(
    name="task_create",
    description="Create an in-memory task for the current process.",
    parameters=object_schema(
        {
            "title": {"type": "string", "description": "Task title."},
            "description": {"type": "string", "description": "Task details.", "default": ""},
            "status": {"type": "string", "description": "Task status.", "default": "pending"},
        },
        required=["title"],
    ),
    handler=task_create,
    read_only=False,
)
