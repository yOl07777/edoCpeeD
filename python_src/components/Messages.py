from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, safe_int, scalar_arg


async def Messages(*args: Any, **kwargs: Any) -> Any:
    messages = normalize_items(option(args, kwargs, "messages", scalar_arg(args, [])))
    start = await computeSliceStart(messages=messages, window=option(args, kwargs, "window", len(messages)))
    visible = messages[start:]
    return component_payload("messages", messages=visible, count=len(visible), total=len(messages), sliceStart=start)


async def computeSliceStart(*args: Any, **kwargs: Any) -> Any:
    messages = normalize_items(option(args, kwargs, "messages", scalar_arg(args, [])))
    window = safe_int(option(args, kwargs, "window", option(args, kwargs, "limit", len(messages))), len(messages))
    return max(0, len(messages) - max(0, window))


async def dropTextInBriefTurns(*args: Any, **kwargs: Any) -> Any:
    messages = normalize_items(option(args, kwargs, "messages", scalar_arg(args, [])))
    for message in messages:
        if message.get("brief") and "text" in message:
            message["text"] = ""
    return messages


async def filterForBriefTool(*args: Any, **kwargs: Any) -> Any:
    messages = normalize_items(option(args, kwargs, "messages", scalar_arg(args, [])))
    return [message for message in messages if not (message.get("toolName") == "brief" or message.get("name") == "brief")]


async def shouldRenderStatically(*args: Any, **kwargs: Any) -> Any:
    return bool(option(args, kwargs, "static", False)) or not bool(option(args, kwargs, "streaming", False))


__all__ = ["Messages", "computeSliceStart", "dropTextInBriefTurns", "filterForBriefTool", "shouldRenderStatically"]
