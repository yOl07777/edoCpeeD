from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, safe_int, scalar_arg


async def MessageSelector(*args: Any, **kwargs: Any) -> Any:
    messages = normalize_items(option(args, kwargs, "messages", scalar_arg(args, [])))
    selectable = await selectableUserMessagesFilter(messages)
    selected_index = safe_int(option(args, kwargs, "selectedIndex", option(args, kwargs, "selected", 0)), 0)
    return component_payload("message_selector", messages=selectable, selectedIndex=selected_index, selected=selectable[selected_index] if 0 <= selected_index < len(selectable) else None)


async def messagesAfterAreOnlySynthetic(*args: Any, **kwargs: Any) -> Any:
    messages = normalize_items(option(args, kwargs, "messages", args[0] if args else []))
    index = safe_int(option(args, kwargs, "index", args[1] if len(args) > 1 else -1), -1)
    return all(bool(message.get("synthetic")) for message in messages[index + 1 :])


async def selectableUserMessagesFilter(*args: Any, **kwargs: Any) -> Any:
    messages = normalize_items(option(args, kwargs, "messages", scalar_arg(args, [])))
    return [message for message in messages if str(message.get("role", "")).lower() == "user" and not message.get("synthetic")]


__all__ = ["MessageSelector", "messagesAfterAreOnlySynthetic", "selectableUserMessagesFilter"]
