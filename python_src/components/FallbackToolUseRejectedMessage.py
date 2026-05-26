from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def FallbackToolUseRejectedMessage(*args: Any, **kwargs: Any) -> Any:
    tool = str(option(args, kwargs, "toolName", option(args, kwargs, "tool", "tool")))
    reason = str(option(args, kwargs, "reason", scalar_arg(args, "rejected by user")))
    return component_payload("fallback_tool_use_rejected_message", toolName=tool, reason=reason, summary=f"{tool} rejected")


__all__ = ["FallbackToolUseRejectedMessage"]
