from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.schedule_store import create_cron


async def cron_create(name: str, prompt: str, schedule: str) -> dict[str, Any]:
    return create_cron(name, prompt, schedule).to_dict()


CronCreateTool = PythonTool(
    name="cron_create",
    description="Create an in-memory scheduled task record.",
    parameters=object_schema(
        {
            "name": {"type": "string"},
            "prompt": {"type": "string"},
            "schedule": {"type": "string", "description": "Human schedule or RRULE text."},
        },
        required=["name", "prompt", "schedule"],
    ),
    handler=cron_create,
    read_only=False,
)
