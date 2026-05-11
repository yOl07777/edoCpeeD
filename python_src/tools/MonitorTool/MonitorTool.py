from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.schedule_store import create_monitor, delete_monitor, list_monitors


async def monitor(
    action: str,
    *,
    name: str | None = None,
    target: str | None = None,
    condition: str | None = None,
    monitor_id: str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    if action == "create":
        if not name or not target or not condition:
            raise ValueError("name, target, and condition are required")
        return create_monitor(name, target, condition).to_dict()
    if action == "list":
        records = [record.to_dict() for record in list_monitors(status=status)]
        return {"count": len(records), "monitors": records}
    if action == "delete":
        if not monitor_id:
            raise ValueError("monitor_id is required")
        return delete_monitor(monitor_id).to_dict()
    raise ValueError(f"Unknown monitor action: {action}")


MonitorTool = PythonTool(
    name="monitor",
    description="Create, list, or delete lightweight monitor records.",
    parameters=object_schema(
        {
            "action": {"type": "string", "enum": ["create", "list", "delete"]},
            "name": {"type": "string"},
            "target": {"type": "string"},
            "condition": {"type": "string"},
            "monitor_id": {"type": "string"},
            "status": {"type": "string"},
        },
        required=["action"],
    ),
    handler=monitor,
    read_only=False,
)
