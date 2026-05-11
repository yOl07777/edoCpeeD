from __future__ import annotations

import asyncio
from typing import Any

from python_src.tools.base import PythonTool, object_schema


async def sleep_tool(seconds: float, *, reason: str = "") -> dict[str, Any]:
    if seconds < 0:
        raise ValueError("seconds must be non-negative")
    if seconds > 60:
        raise ValueError("sleep_tool is capped at 60 seconds")
    await asyncio.sleep(seconds)
    return {"slept_seconds": seconds, "reason": reason}


SleepTool = PythonTool(
    name="sleep",
    description="Wait for a short duration, capped at 60 seconds.",
    parameters=object_schema(
        {
            "seconds": {"type": "number"},
            "reason": {"type": "string", "default": ""},
        },
        required=["seconds"],
    ),
    handler=sleep_tool,
    read_only=True,
)
