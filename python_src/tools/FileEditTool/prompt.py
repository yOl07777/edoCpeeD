"""Prompt text for FileEditTool."""

from __future__ import annotations

from typing import Any


async def getEditToolDescription(*args: Any, **kwargs: Any) -> str:
    tool_name = kwargs.get("toolName") or kwargs.get("tool_name") or "edit_file"
    return (
        "Edit a workspace file by replacing exact UTF-8 text. Provide enough unchanged context in old_text "
        f"to make the edit unique; use replace_all only when every occurrence should change. Tool name: {tool_name}."
    )


__all__ = ["getEditToolDescription"]
