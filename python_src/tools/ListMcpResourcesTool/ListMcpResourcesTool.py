from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.mcp_resource_store import list_resources


async def list_mcp_resources(server: str | None = None) -> dict[str, Any]:
    resources = [resource.summary() for resource in list_resources(server=server)]
    return {"count": len(resources), "resources": resources}


ListMcpResourcesTool = PythonTool(
    name="list_mcp_resources",
    description="List locally registered MCP-style resources.",
    parameters=object_schema(
        {"server": {"type": "string", "description": "Optional server filter."}},
    ),
    handler=list_mcp_resources,
    read_only=True,
)
