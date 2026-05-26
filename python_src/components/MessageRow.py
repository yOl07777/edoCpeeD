from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, first_options, normalize_items, option, scalar_arg
from python_src.components.Message import Message


async def MessageRow(*args: Any, **kwargs: Any) -> Any:
    message = option(args, kwargs, "message", scalar_arg(args, first_options(args)))
    return component_payload("message_row", message=await Message(message), streaming=await isMessageStreaming(message), toolsResolved=await allToolsResolved(message))


async def allToolsResolved(*args: Any, **kwargs: Any) -> Any:
    message = option(args, kwargs, "message", scalar_arg(args, first_options(args)))
    calls = []
    if isinstance(message, dict):
        calls = message.get("tool_calls") or message.get("toolCalls") or []
    return all(bool(call.get("resolved") or call.get("result") or call.get("status") in {"done", "success"}) for call in calls)


async def areMessageRowPropsEqual(*args: Any, **kwargs: Any) -> Any:
    left = option(args, kwargs, "left", args[0] if args else None)
    right = option(args, kwargs, "right", args[1] if len(args) > 1 else None)
    return left == right


async def hasContentAfterIndex(*args: Any, **kwargs: Any) -> Any:
    messages = normalize_items(option(args, kwargs, "messages", args[0] if args else []))
    index = int(option(args, kwargs, "index", args[1] if len(args) > 1 else -1) or -1)
    return any(str(row.get("text", row.get("content", ""))).strip() for row in messages[index + 1 :])


async def isMessageStreaming(*args: Any, **kwargs: Any) -> Any:
    message = option(args, kwargs, "message", scalar_arg(args, first_options(args)))
    return bool(isinstance(message, dict) and (message.get("streaming") or message.get("status") == "streaming"))


__all__ = ["MessageRow", "allToolsResolved", "areMessageRowPropsEqual", "hasContentAfterIndex", "isMessageStreaming"]
