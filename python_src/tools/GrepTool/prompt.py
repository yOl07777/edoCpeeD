"""Prompt text for GrepTool."""

from __future__ import annotations

from typing import Any

GREP_TOOL_NAME = "grep_files"
DESCRIPTION = (
    "Search workspace text files with a Python regular expression. Prefer include patterns "
    "that narrow the search to relevant source files."
)


async def getDescription(*args: Any, **kwargs: Any) -> str:
    tool_name = kwargs.get("toolName") or kwargs.get("tool_name") or GREP_TOOL_NAME
    return f"{DESCRIPTION} Tool name: {tool_name}."


__all__ = ["DESCRIPTION", "GREP_TOOL_NAME", "getDescription"]
