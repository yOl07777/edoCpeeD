from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, first_options, option, scalar_arg


def _message_text(message: Any) -> str:
    if isinstance(message, dict):
        content = message.get("content", message.get("text", ""))
        if isinstance(content, list):
            return "\n".join(str(block.get("text", block)) if isinstance(block, dict) else str(block) for block in content)
        return str(content)
    return str(message or "")


async def Message(*args: Any, **kwargs: Any) -> Any:
    message = option(args, kwargs, "message", scalar_arg(args, first_options(args)))
    role = str(message.get("role", option(args, kwargs, "role", "assistant"))) if isinstance(message, dict) else str(option(args, kwargs, "role", "assistant"))
    text = _message_text(message)
    return component_payload("message", role=role, text=text, hasThinking=await hasThinkingContent(message))


async def areMessagePropsEqual(*args: Any, **kwargs: Any) -> Any:
    left = option(args, kwargs, "left", args[0] if args else None)
    right = option(args, kwargs, "right", args[1] if len(args) > 1 else None)
    return left == right


async def hasThinkingContent(*args: Any, **kwargs: Any) -> Any:
    message = option(args, kwargs, "message", scalar_arg(args, first_options(args)))
    if isinstance(message, dict):
        if message.get("thinking") or message.get("reasoning"):
            return True
        content = message.get("content", [])
        if isinstance(content, list):
            return any(isinstance(block, dict) and str(block.get("type", "")).lower() in {"thinking", "reasoning"} for block in content)
    return False


__all__ = ["Message", "areMessagePropsEqual", "hasThinkingContent"]
