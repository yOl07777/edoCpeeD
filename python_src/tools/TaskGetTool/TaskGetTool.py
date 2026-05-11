from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.task_store import get_task


async def task_get(task_id: str) -> dict[str, Any]:
    return get_task(task_id).to_dict()


TaskGetTool = PythonTool(
    name="task_get",
    description="Get a task by id.",
    parameters=object_schema(
        {"task_id": {"type": "string", "description": "Task id."}},
        required=["task_id"],
    ),
    handler=task_get,
    read_only=True,
)
