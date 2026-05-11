from __future__ import annotations

from typing import Any

from python_src.tools.agent_store import send_message
from python_src.tools.base import PythonTool, object_schema


async def send_agent_message(target_id: str, content: str, *, sender: str = "user") -> dict[str, Any]:
    return send_message(target_id, content, sender=sender)


SendMessageTool = PythonTool(
    name="send_message",
    description="Send a message to an in-process agent or team.",
    parameters=object_schema(
        {
            "target_id": {"type": "string"},
            "content": {"type": "string"},
            "sender": {"type": "string", "default": "user"},
        },
        required=["target_id", "content"],
    ),
    handler=send_agent_message,
    read_only=False,
)
