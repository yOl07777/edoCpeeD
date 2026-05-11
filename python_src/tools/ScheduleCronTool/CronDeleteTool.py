from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.schedule_store import delete_cron


async def cron_delete(cron_id: str) -> dict[str, Any]:
    return delete_cron(cron_id).to_dict()


CronDeleteTool = PythonTool(
    name="cron_delete",
    description="Delete an in-memory scheduled task record.",
    parameters=object_schema({"cron_id": {"type": "string"}}, required=["cron_id"]),
    handler=cron_delete,
    read_only=False,
)
