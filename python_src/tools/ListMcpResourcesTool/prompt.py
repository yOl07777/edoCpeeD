"""Prompt text for ListMcpResourcesTool."""

from __future__ import annotations

LIST_MCP_RESOURCES_TOOL_NAME = "list_mcp_resources"
DESCRIPTION = "List locally registered MCP-style resources, optionally filtered by server."
PROMPT = "Use this before read_mcp_resource when the exact resource URI is unknown."

__all__ = ["DESCRIPTION", "LIST_MCP_RESOURCES_TOOL_NAME", "PROMPT"]
