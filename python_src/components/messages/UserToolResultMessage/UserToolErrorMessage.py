from __future__ import annotations

from typing import Any

from python_src.components.messages.UserToolResultMessage._shared import coerce_tool_result, summary_for, tool_result_payload


async def UserToolErrorMessage(*args: Any, **kwargs: Any) -> Any:
    extra = {key: value for key, value in kwargs.items() if key != "error"}
    result = coerce_tool_result(kwargs.get("result") or (args[0] if args else None), status="error", error=kwargs.get("error"), **extra)
    return tool_result_payload("user_tool_error_message", result=result, summary=summary_for(result))


__all__ = ["UserToolErrorMessage"]
