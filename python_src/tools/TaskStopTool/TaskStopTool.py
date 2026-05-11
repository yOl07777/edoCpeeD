from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.task_store import stop_task


async def task_stop(task_id: str, *, reason: str = "") -> dict[str, Any]:
    return stop_task(task_id, reason=reason).to_dict()


TaskStopTool = PythonTool(
    name="task_stop",
    description="Mark a task as stopped.",
    parameters=object_schema(
        {
            "task_id": {"type": "string", "description": "Task id."},
            "reason": {"type": "string", "description": "Optional stop reason.", "default": ""},
        },
        required=["task_id"],
    ),
    handler=task_stop,
    read_only=False,
)
