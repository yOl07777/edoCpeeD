"""Prompt text for WebSearchTool."""

from __future__ import annotations

from typing import Any

WEB_SEARCH_TOOL_NAME = "web_search"
DESCRIPTION = "Search the web and return result titles and URLs for current or external information."


async def getWebSearchPrompt(*args: Any, **kwargs: Any) -> str:
    query = kwargs.get("query") or (args[0] if args else "")
    limit = kwargs.get("limit", 5)
    return f"Search query: {query}\nReturn up to {limit} relevant results with titles and URLs."


__all__ = ["DESCRIPTION", "WEB_SEARCH_TOOL_NAME", "getWebSearchPrompt"]
