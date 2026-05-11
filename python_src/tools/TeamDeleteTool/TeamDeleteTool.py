from __future__ import annotations

from typing import Any

from python_src.tools.agent_store import delete_team
from python_src.tools.base import PythonTool, object_schema


async def team_delete(team_id: str) -> dict[str, Any]:
    return delete_team(team_id).to_dict()


TeamDeleteTool = PythonTool(
    name="team_delete",
    description="Delete a lightweight in-process team.",
    parameters=object_schema(
        {"team_id": {"type": "string"}},
        required=["team_id"],
    ),
    handler=team_delete,
    read_only=False,
)
