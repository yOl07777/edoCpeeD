from __future__ import annotations

from typing import Any

from python_src.tools.agent_store import create_team
from python_src.tools.base import PythonTool, object_schema


async def team_create(name: str, agent_ids: list[str] | None = None) -> dict[str, Any]:
    return create_team(name, agent_ids).to_dict()


TeamCreateTool = PythonTool(
    name="team_create",
    description="Create a lightweight in-process team from agent ids.",
    parameters=object_schema(
        {
            "name": {"type": "string"},
            "agent_ids": {"type": "array", "items": {"type": "string"}},
        },
        required=["name"],
    ),
    handler=team_create,
    read_only=False,
)
