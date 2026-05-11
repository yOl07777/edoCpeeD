from __future__ import annotations

import json
from typing import Any, Literal

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.path_utils import resolve_workspace_path

TodoStatus = Literal["pending", "in_progress", "completed"]


async def todo_write(
    todos: list[dict[str, Any]],
    *,
    path: str = ".deepseek_todos.json",
    cwd: str | None = None,
) -> dict[str, Any]:
    normalized: list[dict[str, str]] = []
    for index, todo in enumerate(todos, start=1):
        content = str(todo.get("content", "")).strip()
        status = str(todo.get("status", "pending"))
        if not content:
            raise ValueError(f"Todo #{index} has empty content")
        if status not in {"pending", "in_progress", "completed"}:
            raise ValueError(f"Todo #{index} has invalid status: {status}")
        normalized.append(
            {
                "id": str(todo.get("id") or index),
                "content": content,
                "status": status,
            }
        )
    target = resolve_workspace_path(path, cwd=cwd)
    target.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "path": str(target),
        "count": len(normalized),
        "todos": normalized,
    }


TodoWriteTool = PythonTool(
    name="todo_write",
    description="Create or replace the local todo list for the current task.",
    parameters=object_schema(
        {
            "todos": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "content": {"type": "string"},
                        "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                    },
                    "required": ["content", "status"],
                    "additionalProperties": False,
                },
            },
            "path": {"type": "string", "description": "Workspace-relative todo file path.", "default": ".deepseek_todos.json"},
        },
        required=["todos"],
    ),
    handler=todo_write,
    read_only=False,
)
