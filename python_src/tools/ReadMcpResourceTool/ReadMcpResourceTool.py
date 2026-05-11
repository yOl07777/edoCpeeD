from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.mcp_resource_store import read_resource


async def read_mcp_resource(uri: str) -> dict[str, Any]:
    return read_resource(uri).to_dict()


inputSchema = object_schema({"uri": {"type": "string"}}, required=["uri"])
outputSchema = {"type": "object"}

ReadMcpResourceTool = PythonTool(
    name="read_mcp_resource",
    description="Read a locally registered MCP-style resource by URI.",
    parameters=inputSchema,
    handler=read_mcp_resource,
    read_only=True,
)
