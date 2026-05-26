"""Prompt text for FileReadTool."""

from __future__ import annotations

from typing import Any

FILE_READ_TOOL_NAME = "read_file"
MAX_LINES_TO_READ = 2_000
FILE_UNCHANGED_STUB = "<file unchanged>"
LINE_FORMAT_INSTRUCTION = "Return UTF-8 text with original line order preserved."
OFFSET_INSTRUCTION_DEFAULT = "Use offset and limit when reading large files."
OFFSET_INSTRUCTION_TARGETED = "For targeted reads, set offset to the first relevant zero-based line."
DESCRIPTION = (
    "Read a UTF-8 text file inside the current workspace. Use offset/limit for large files "
    "and prefer targeted reads after locating relevant lines."
)


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


async def renderPromptTemplate(*args: Any, **kwargs: Any) -> str:
    data = _payload(args, kwargs)
    max_lines = int(data.get("maxLines") or data.get("max_lines") or MAX_LINES_TO_READ)
    targeted = bool(data.get("targeted", False))
    offset_instruction = OFFSET_INSTRUCTION_TARGETED if targeted else OFFSET_INSTRUCTION_DEFAULT
    return (
        f"{DESCRIPTION}\n"
        f"- Tool name: {data.get('toolName') or FILE_READ_TOOL_NAME}\n"
        f"- Maximum suggested read: {max_lines} lines\n"
        f"- {LINE_FORMAT_INSTRUCTION}\n"
        f"- {offset_instruction}"
    )


__all__ = [
    "DESCRIPTION",
    "FILE_READ_TOOL_NAME",
    "FILE_UNCHANGED_STUB",
    "LINE_FORMAT_INSTRUCTION",
    "MAX_LINES_TO_READ",
    "OFFSET_INSTRUCTION_DEFAULT",
    "OFFSET_INSTRUCTION_TARGETED",
    "renderPromptTemplate",
]
