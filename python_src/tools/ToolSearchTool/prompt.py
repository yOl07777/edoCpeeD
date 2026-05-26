"""Prompt helpers for ToolSearchTool."""

from __future__ import annotations

from typing import Any

from python_src.tools.ToolSearchTool.constants import TOOL_SEARCH_TOOL_NAME


async def isDeferredTool(*args: Any, **kwargs: Any) -> bool:
    value = args[0] if args else kwargs
    if isinstance(value, dict):
        return bool(value.get("deferred") or value.get("is_deferred") or value.get("source") == "deferred")
    return False


async def formatDeferredToolLine(*args: Any, **kwargs: Any) -> str:
    value = args[0] if args else kwargs
    if isinstance(value, dict):
        name = value.get("name") or value.get("tool") or "tool"
        description = value.get("description") or ""
    else:
        name, description = str(value), ""
    return f"- {name}: {description}".rstrip()


async def getPrompt(*args: Any, **kwargs: Any) -> str:
    tools = list(args[0] if args else kwargs.get("tools", []) or [])
    lines = [await formatDeferredToolLine(tool) for tool in tools if await isDeferredTool(tool)]
    body = "\n".join(lines)
    return (
        f"Use {TOOL_SEARCH_TOOL_NAME} to discover deferred/local tools by name or description. "
        "Call it before assuming a tool is unavailable."
        + (f"\n{body}" if body else "")
    )


__all__ = ["formatDeferredToolLine", "getPrompt", "isDeferredTool"]
