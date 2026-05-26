"""Prompt text for FileWriteTool."""

from __future__ import annotations

from typing import Any

FILE_WRITE_TOOL_NAME = "write_file"
DESCRIPTION = (
    "Write UTF-8 text to a file inside the current workspace. Create parent directories when needed "
    "and avoid overwriting user work unless the requested content is complete."
)


async def getWriteToolDescription(*args: Any, **kwargs: Any) -> str:
    tool_name = kwargs.get("toolName") or kwargs.get("tool_name") or FILE_WRITE_TOOL_NAME
    return f"{DESCRIPTION} Tool name: {tool_name}."


__all__ = ["DESCRIPTION", "FILE_WRITE_TOOL_NAME", "getWriteToolDescription"]
