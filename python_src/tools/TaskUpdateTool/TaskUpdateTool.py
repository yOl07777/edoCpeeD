from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.task_store import update_task


async def task_update(
    task_id: str,
    *,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    return update_task(
        task_id,
        title=title,
        description=description,
        status=status,
    ).to_dict()


TaskUpdateTool = PythonTool(
    name="task_update",
    description="Update task fields.",
    parameters=object_schema(
        {
            "task_id": {"type": "string", "description": "Task id."},
            "title": {"type": "string", "description": "New task title."},
            "description": {"type": "string", "description": "New task details."},
            "status": {"type": "string", "description": "New task status."},
        },
        required=["task_id"],
    ),
    handler=task_update,
    read_only=False,
)
