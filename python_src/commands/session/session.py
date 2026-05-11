from __future__ import annotations

from typing import Any

from python_src.session_store import SESSION_STATE
from python_src.tools.base import PythonTool, object_schema


async def session_command(
    action: str,
    *,
    role: str = "user",
    content: str = "",
) -> dict[str, Any]:
    if action == "add":
        return {"message": SESSION_STATE.add(role, content)}
    if action == "list":
        return {"count": len(SESSION_STATE.messages), "messages": list(SESSION_STATE.messages)}
    if action == "export":
        return {"jsonl": SESSION_STATE.export_jsonl()}
    if action == "clear":
        return {"cleared": SESSION_STATE.clear()}
    raise ValueError(f"Unknown session action: {action}")


call = PythonTool(
    name="session",
    description="Manage the lightweight in-process conversation session.",
    parameters=object_schema(
        {
            "action": {"type": "string", "enum": ["add", "list", "export", "clear"]},
            "role": {"type": "string", "default": "user"},
            "content": {"type": "string"},
        },
        required=["action"],
    ),
    handler=session_command,
    read_only=False,
)
