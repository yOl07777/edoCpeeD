"""Generic MCP tool dry-run wrapper."""

from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema

inputSchema = object_schema(
    {
        "server": {"type": "string", "description": "MCP server name."},
        "tool": {"type": "string", "description": "MCP tool name."},
        "arguments": {"type": "object", "description": "Tool arguments."},
    },
    required=["server", "tool"],
)
outputSchema = {"type": "object"}


async def call_mcp_tool(server: str, tool: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "ok": False,
        "server": server,
        "tool": tool,
        "arguments": arguments or {},
        "dry_run": True,
        "message": "Generic MCP tool execution is not connected in this Python migration shim.",
    }


MCPTool = PythonTool(
    name="mcp_tool",
    description="Dry-run wrapper for an MCP server tool call.",
    parameters=inputSchema,
    handler=call_mcp_tool,
    read_only=False,
)

__all__ = ["MCPTool", "call_mcp_tool", "inputSchema", "outputSchema"]
