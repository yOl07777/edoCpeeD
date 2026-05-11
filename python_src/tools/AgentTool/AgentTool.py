from __future__ import annotations

from typing import Any

from python_src.tools.agent_store import AGENTS, create_agent, get_agent
from python_src.tools.base import PythonTool, object_schema


async def agent(
    action: str,
    *,
    name: str | None = None,
    prompt: str = "",
    agent_id: str | None = None,
) -> dict[str, Any]:
    if action == "create":
        if not name:
            raise ValueError("name is required for create")
        return create_agent(name, prompt).to_dict()
    if action == "get":
        if not agent_id:
            raise ValueError("agent_id is required for get")
        return get_agent(agent_id).to_dict()
    if action == "list":
        return {"count": len(AGENTS), "agents": [agent.to_dict() for agent in AGENTS.values()]}
    raise ValueError(f"Unknown agent action: {action}")


inputSchema = object_schema(
    {
        "action": {"type": "string", "enum": ["create", "get", "list"]},
        "name": {"type": "string"},
        "prompt": {"type": "string"},
        "agent_id": {"type": "string"},
    },
    required=["action"],
)
outputSchema = {"type": "object"}

AgentTool = PythonTool(
    name="agent",
    description="Create, list, or inspect lightweight in-process agents.",
    parameters=inputSchema,
    handler=agent,
    read_only=False,
)
