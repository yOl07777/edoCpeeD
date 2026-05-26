from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def StatusLine(*args: Any, **kwargs: Any) -> Any:
    messages = option(args, kwargs, "messages", scalar_arg(args, []))
    model = str(option(args, kwargs, "model", "deepseek-chat"))
    last_id = await getLastAssistantMessageId(messages)
    return component_payload("status_line", model=model, lastAssistantMessageId=last_id, visible=await statusLineShouldDisplay(messages=messages, model=model))


async def getLastAssistantMessageId(*args: Any, **kwargs: Any) -> Any:
    messages = normalize_items(option(args, kwargs, "messages", scalar_arg(args, [])))
    for message in reversed(messages):
        if str(message.get("role", "")).lower() == "assistant":
            return message.get("id") or message.get("message_id")
    return None


async def statusLineShouldDisplay(*args: Any, **kwargs: Any) -> Any:
    if option(args, kwargs, "visible", None) is not None:
        return bool(option(args, kwargs, "visible"))
    return bool(option(args, kwargs, "model", None) or option(args, kwargs, "messages", None))


__all__ = ["StatusLine", "getLastAssistantMessageId", "statusLineShouldDisplay"]
