from __future__ import annotations

from typing import Any

from python_src.components.messages.UserToolResultMessage._shared import coerce_tool_result


async def useGetToolFromMessages(*args: Any, **kwargs: Any) -> Any:
    messages = kwargs.get("messages") or (args[0] if args else []) or []
    tool_use_id = kwargs.get("toolUseId") or kwargs.get("tool_call_id")
    for message in messages:
        content = message.get("content") if isinstance(message, dict) else None
        blocks = content if isinstance(content, list) else [content]
        for block in blocks:
            if isinstance(block, dict):
                result = coerce_tool_result(block)
                if not tool_use_id or result.get("toolUseId") == tool_use_id:
                    return result
    return None


__all__ = ["useGetToolFromMessages"]
