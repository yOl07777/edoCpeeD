from __future__ import annotations

from typing import Any


HOOK_TIMING_DISPLAY_THRESHOLD_MS = 250


async def buildSchemaNotSentHint(tool_name: str) -> str:
    return f"Tool schema for `{tool_name}` was not sent to the model; enable tools or register the tool first."


async def classifyToolError(error: BaseException | str) -> dict[str, Any]:
    text = str(error)
    lower = text.lower()
    if isinstance(error, PermissionError) or "permission" in lower or "denied" in lower:
        kind = "permission"
    elif isinstance(error, TimeoutError) or "timeout" in lower or "timed out" in lower:
        kind = "timeout"
    elif isinstance(error, FileNotFoundError) or "not found" in lower:
        kind = "not_found"
    elif isinstance(error, ValueError):
        kind = "validation"
    else:
        kind = "runtime"
    return {"kind": kind, "message": text, "retryable": kind in {"timeout", "runtime"}}
