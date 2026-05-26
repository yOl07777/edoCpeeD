from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def FallbackToolUseErrorMessage(*args: Any, **kwargs: Any) -> Any:
    tool = str(option(args, kwargs, "toolName", option(args, kwargs, "tool", "tool")))
    error = str(option(args, kwargs, "error", scalar_arg(args, "unknown error")))
    return component_payload("fallback_tool_use_error_message", toolName=tool, error=error, summary=f"{tool} failed: {error}")


__all__ = ["FallbackToolUseErrorMessage"]
