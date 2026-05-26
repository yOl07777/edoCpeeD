"""Local tool search shim."""

from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.ToolSearchTool.constants import TOOL_SEARCH_TOOL_NAME

inputSchema = object_schema(
    {
        "query": {"type": "string"},
        "limit": {"type": "integer", "default": 8},
    },
    required=["query"],
)
outputSchema = {"type": "object"}

_DESCRIPTION_CACHE: dict[str, str] = {}
_REGISTERED_TOOLS: list[PythonTool] = []


def registerToolForSearch(tool: PythonTool) -> PythonTool:
    if all(existing.name != tool.name for existing in _REGISTERED_TOOLS):
        _REGISTERED_TOOLS.append(tool)
    _DESCRIPTION_CACHE[tool.name] = tool.description
    return tool


async def clearToolSearchDescriptionCache(*args: Any, **kwargs: Any) -> dict[str, int]:
    count = len(_DESCRIPTION_CACHE)
    _DESCRIPTION_CACHE.clear()
    return {"cleared": count}


async def tool_search(query: str, *, limit: int = 8, tools: list[PythonTool | dict[str, Any]] | None = None) -> dict[str, Any]:
    candidates = tools or _REGISTERED_TOOLS
    needle = query.lower()
    scored: list[dict[str, Any]] = []
    for tool in candidates:
        if isinstance(tool, PythonTool):
            name, description = tool.name, tool.description
        else:
            name, description = str(tool.get("name", "")), str(tool.get("description", ""))
        haystack = f"{name} {description}".lower()
        if needle in haystack:
            score = 2 if needle in name.lower() else 1
            scored.append({"name": name, "description": description, "score": score})
    scored.sort(key=lambda item: (-item["score"], item["name"]))
    return {"query": query, "results": scored[:limit], "count": min(len(scored), limit), "truncated": len(scored) > limit}


ToolSearchTool = PythonTool(
    name=TOOL_SEARCH_TOOL_NAME,
    description="Search locally registered tool descriptions.",
    parameters=inputSchema,
    handler=tool_search,
    read_only=True,
)

__all__ = [
    "ToolSearchTool",
    "clearToolSearchDescriptionCache",
    "inputSchema",
    "outputSchema",
    "registerToolForSearch",
    "tool_search",
]
