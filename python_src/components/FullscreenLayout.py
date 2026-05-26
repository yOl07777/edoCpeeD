from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, safe_int, scalar_arg


ScrollChromeContext: dict[str, Any] = {"type": "scroll_chrome_context", "provider": "deepseek"}


async def FullscreenLayout(*args: Any, **kwargs: Any) -> Any:
    messages = normalize_items(option(args, kwargs, "messages", scalar_arg(args, [])))
    divider = await useUnseenDivider(messages=messages, lastSeenIndex=option(args, kwargs, "lastSeenIndex", -1))
    return component_payload("fullscreen_layout", messages=messages, divider=divider, count=len(messages))


async def computeUnseenDivider(*args: Any, **kwargs: Any) -> Any:
    messages = normalize_items(option(args, kwargs, "messages", scalar_arg(args, [])))
    last_seen = safe_int(option(args, kwargs, "lastSeenIndex", option(args, kwargs, "last_seen_index", -1)), -1)
    unseen = await countUnseenAssistantTurns(messages=messages, lastSeenIndex=last_seen)
    return {"index": last_seen + 1 if unseen else None, "unseenAssistantTurns": unseen}


async def countUnseenAssistantTurns(*args: Any, **kwargs: Any) -> Any:
    messages = normalize_items(option(args, kwargs, "messages", scalar_arg(args, [])))
    last_seen = safe_int(option(args, kwargs, "lastSeenIndex", option(args, kwargs, "last_seen_index", -1)), -1)
    unseen = messages[last_seen + 1 :] if last_seen + 1 < len(messages) else []
    return sum(1 for message in unseen if str(message.get("role", "")).lower() == "assistant")


async def useUnseenDivider(*args: Any, **kwargs: Any) -> Any:
    divider = await computeUnseenDivider(*args, **kwargs)
    return component_payload("unseen_divider", visible=bool(divider["unseenAssistantTurns"]), **divider)


__all__ = ["ScrollChromeContext", "FullscreenLayout", "computeUnseenDivider", "countUnseenAssistantTurns", "useUnseenDivider"]
