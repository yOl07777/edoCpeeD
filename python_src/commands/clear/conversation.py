from __future__ import annotations

from typing import Any

from python_src.session_store import SESSION_STATE
from python_src.tools.base import PythonTool, object_schema


def clearConversation() -> dict[str, Any]:
    return {"cleared": SESSION_STATE.clear()}


async def clear_conversation() -> dict[str, Any]:
    return clearConversation()


call = PythonTool(
    name="clear_conversation",
    description="Clear the lightweight in-process conversation session.",
    parameters=object_schema({}),
    handler=clear_conversation,
    read_only=False,
)
