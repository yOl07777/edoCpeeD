"""MCP auth tool dry-run shim."""

from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema

MCP_AUTH_TOOL_NAME = "mcp_auth"


async def mcp_auth(server: str, *, action: str = "status") -> dict[str, Any]:
    return {
        "server": server,
        "action": action,
        "authenticated": False,
        "dry_run": True,
        "message": "MCP auth is not connected in this Python migration shim.",
    }


async def createMcpAuthTool(*args: Any, **kwargs: Any) -> PythonTool:
    return PythonTool(
        name=kwargs.get("name") or MCP_AUTH_TOOL_NAME,
        description="Dry-run MCP authentication helper.",
        parameters=object_schema(
            {
                "server": {"type": "string"},
                "action": {"type": "string", "enum": ["status", "login", "logout"], "default": "status"},
            },
            required=["server"],
        ),
        handler=mcp_auth,
        read_only=False,
    )


McpAuthTool = PythonTool(
    name=MCP_AUTH_TOOL_NAME,
    description="Dry-run MCP authentication helper.",
    parameters=object_schema(
        {
            "server": {"type": "string"},
            "action": {"type": "string", "enum": ["status", "login", "logout"], "default": "status"},
        },
        required=["server"],
    ),
    handler=mcp_auth,
    read_only=False,
)

__all__ = ["MCP_AUTH_TOOL_NAME", "McpAuthTool", "createMcpAuthTool", "mcp_auth"]
