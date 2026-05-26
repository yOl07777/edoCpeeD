"""String helpers for MCP tool names used by the Python migration."""

from __future__ import annotations

from typing import Any

from .normalization import normalizeNameForMCP

MCP_TOOL_PREFIX = "mcp__"


def _read_name(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("name") or value.get("serverName") or value.get("id") or "")
    return str(value or "")


async def buildMcpToolName(server_name: Any, tool_name: Any | None = None) -> str:
    """Build the OpenAI/DeepSeek-safe MCP tool name ``mcp__server__tool``."""

    server = await normalizeNameForMCP(_read_name(server_name))
    tool = await normalizeNameForMCP(_read_name(tool_name) if tool_name is not None else "")
    return f"{MCP_TOOL_PREFIX}{server}__{tool}" if tool else f"{MCP_TOOL_PREFIX}{server}"


async def extractMcpToolDisplayName(tool_name: str) -> str:
    """Extract the original display portion from an MCP tool name."""

    info = await mcpInfoFromString(tool_name)
    return info.get("toolName") or str(tool_name or "")


async def getMcpDisplayName(value: Any) -> str:
    """Return a human-readable display name for a server, command, or tool."""

    if isinstance(value, dict):
        for key in ("displayName", "title", "name", "serverName", "id"):
            if value.get(key):
                return str(value[key])
    return str(value or "")


async def getMcpPrefix(server_name: Any) -> str:
    """Return the MCP prefix used for all tools belonging to a server."""

    server = await normalizeNameForMCP(_read_name(server_name))
    return f"{MCP_TOOL_PREFIX}{server}__"


async def getToolNameForPermissionCheck(tool: Any) -> str:
    """Return the canonical tool name used by permission checks."""

    if isinstance(tool, dict):
        if tool.get("permissionName"):
            return str(tool["permissionName"])
        if tool.get("serverName") and tool.get("name"):
            return await buildMcpToolName(tool["serverName"], tool["name"])
        return str(tool.get("name") or "")
    return str(tool or "")


async def mcpInfoFromString(tool_name: str) -> dict[str, str | bool | None]:
    """Parse an MCP tool string into server/tool components."""

    value = str(tool_name or "")
    if not value.startswith(MCP_TOOL_PREFIX):
        return {"isMcp": False, "serverName": None, "toolName": value}
    rest = value[len(MCP_TOOL_PREFIX) :]
    server, _, tool = rest.partition("__")
    return {"isMcp": True, "serverName": server or None, "toolName": tool or None}
