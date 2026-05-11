from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.schedule_store import list_crons


async def cron_list(status: str | None = None) -> dict[str, Any]:
    records = [record.to_dict() for record in list_crons(status=status)]
    return {"count": len(records), "crons": records}


CronListTool = PythonTool(
    name="cron_list",
    description="List in-memory scheduled task records.",
    parameters=object_schema({"status": {"type": "string"}}),
    handler=cron_list,
    read_only=True,
)
