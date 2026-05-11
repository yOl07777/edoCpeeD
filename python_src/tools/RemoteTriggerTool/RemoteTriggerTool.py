from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.schedule_store import create_trigger


async def remote_trigger(name: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return create_trigger(name, payload or {}).to_dict()


RemoteTriggerTool = PythonTool(
    name="remote_trigger",
    description="Record a lightweight remote trigger event.",
    parameters=object_schema(
        {
            "name": {"type": "string"},
            "payload": {"type": "object"},
        },
        required=["name"],
    ),
    handler=remote_trigger,
    read_only=False,
)
