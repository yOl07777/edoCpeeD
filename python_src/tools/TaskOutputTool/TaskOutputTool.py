from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.task_store import append_task_output


async def task_output(task_id: str, content: str) -> dict[str, Any]:
    return append_task_output(task_id, content).to_dict()


TaskOutputTool = PythonTool(
    name="task_output",
    description="Append output text to a task.",
    parameters=object_schema(
        {
            "task_id": {"type": "string", "description": "Task id."},
            "content": {"type": "string", "description": "Output text to append."},
        },
        required=["task_id", "content"],
    ),
    handler=task_output,
    read_only=False,
)
