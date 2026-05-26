from __future__ import annotations

import json
from typing import Any, Callable

from deepseek_code.core.types import InternalToolCall, InternalMessage


def claude_tool_to_deepseek(tool: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool.get("description", ""),
            "parameters": tool.get("input_schema") or tool.get("parameters") or {"type": "object"},
        },
    }


def tools_to_deepseek(tools: list[dict[str, Any]] | None) -> list[dict[str, Any]] | None:
    if not tools:
        return None
    converted: list[dict[str, Any]] = []
    for tool in tools:
        if tool.get("type") == "function" and "function" in tool:
            converted.append(tool)
        else:
            converted.append(claude_tool_to_deepseek(tool))
    return converted


def tool_result_message(tool_call_id: str, content: Any) -> InternalMessage:
    if not isinstance(content, str):
        content = json.dumps(content, ensure_ascii=False)
    return InternalMessage(role="tool", content=content, tool_call_id=tool_call_id)


class ToolRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, handler: Callable[..., Any]) -> None:
        self._handlers[name] = handler

    async def call(self, tool_call: InternalToolCall) -> InternalMessage:
        if tool_call.name not in self._handlers:
            return tool_result_message(tool_call.id, {"error": f"Unknown tool: {tool_call.name}"})
        args = tool_call.arguments
        try:
            if isinstance(args, str):
                args = json.loads(args or "{}")
            result = self._handlers[tool_call.name](**args)
            if hasattr(result, "__await__"):
                result = await result
            return tool_result_message(tool_call.id, result)
        except Exception as error:
            return tool_result_message(
                tool_call.id,
                {
                    "ok": False,
                    "tool": tool_call.name,
                    "error": str(error),
                    "suggestion": "工具调用失败，但对话可以继续。请基于已有信息回答，或尝试其他工具/来源。",
                },
            )
