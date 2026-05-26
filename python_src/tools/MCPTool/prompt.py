"""Prompt text for MCPTool."""

from __future__ import annotations

DESCRIPTION = "Call a tool exposed by a configured MCP server."
PROMPT = (
    "Use MCP tools only when a configured server exposes the required capability. "
    "This Python migration shim records the intended server/tool/arguments without starting a server."
)

__all__ = ["DESCRIPTION", "PROMPT"]
