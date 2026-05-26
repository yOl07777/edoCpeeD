from __future__ import annotations

from typing import Any

from python_src.components.messages.UserToolResultMessage._shared import coerce_tool_result, summary_for, tool_result_payload


async def UserToolRejectMessage(*args: Any, **kwargs: Any) -> Any:
    result = coerce_tool_result(kwargs.get("result") or (args[0] if args else None), status="rejected", **kwargs)
    return tool_result_payload("user_tool_reject_message", result=result, summary=summary_for(result))


__all__ = ["UserToolRejectMessage"]
