from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload


async def AssistantToolUseMessage(*args: Any, **kwargs: Any) -> Any:
    tool = kwargs.get("tool") or (args[0] if args else {}) or {}
    if isinstance(tool, dict):
        name = tool.get("name") or tool.get("function", {}).get("name") or "tool"
        arguments = tool.get("arguments") or tool.get("input") or tool.get("function", {}).get("arguments") or {}
        tool_id = tool.get("id") or tool.get("tool_call_id")
    else:
        name = str(tool)
        arguments = {}
        tool_id = None
    return message_payload("assistant_tool_use_message", role="assistant", toolName=str(name), arguments=arguments, toolUseId=tool_id)


__all__ = ["AssistantToolUseMessage"]
