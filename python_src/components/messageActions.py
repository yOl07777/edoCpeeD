from __future__ import annotations

import re
from typing import Any

from python_src.components._shared import component_payload, first_options, normalize_items, option, scalar_arg


InVirtualListContext: dict[str, Any] = {"type": "virtual_list_context", "provider": "deepseek"}
MESSAGE_ACTIONS: tuple[str, ...] = ("copy", "details", "retry", "select")
MessageActionsSelectedContext: dict[str, Any] = {"type": "message_actions_selected_context", "provider": "deepseek"}


def _content_of(message: Any) -> Any:
    if isinstance(message, dict):
        return message.get("content", message.get("text", ""))
    return message


async def MessageActionsBar(*args: Any, **kwargs: Any) -> Any:
    message = option(args, kwargs, "message", scalar_arg(args, first_options(args)))
    actions = normalize_items(option(args, kwargs, "actions", MESSAGE_ACTIONS), text_key="name")
    return component_payload("message_actions_bar", actions=actions, navigable=await isNavigableMessage(message), selected=bool(option(args, kwargs, "selected", False)))


async def MessageActionsKeybindings(*args: Any, **kwargs: Any) -> Any:
    bindings = {"copy": "c", "details": "d", "retry": "r", "select": "enter"}
    return component_payload("message_actions_keybindings", bindings=bindings)


async def copyTextOf(*args: Any, **kwargs: Any) -> Any:
    message = option(args, kwargs, "message", scalar_arg(args, first_options(args)))
    content = _content_of(message)
    if isinstance(content, list):
        return "\n".join(str(block.get("text", "")) if isinstance(block, dict) else str(block) for block in content)
    return str(content or "")


async def isNavigableMessage(*args: Any, **kwargs: Any) -> Any:
    message = option(args, kwargs, "message", scalar_arg(args, first_options(args)))
    if not message:
        return False
    if isinstance(message, dict) and message.get("synthetic"):
        return False
    return bool(await copyTextOf(message) or await toolCallOf(message))


async def stripSystemReminders(*args: Any, **kwargs: Any) -> Any:
    text = str(option(args, kwargs, "text", scalar_arg(args, "")))
    return re.sub(r"(?is)<system-reminder>.*?</system-reminder>", "", text).strip()


async def toolCallOf(*args: Any, **kwargs: Any) -> Any:
    message = option(args, kwargs, "message", scalar_arg(args, first_options(args)))
    if isinstance(message, dict):
        calls = message.get("tool_calls") or message.get("toolCalls")
        if calls:
            return calls[0]
        content = message.get("content", [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") in {"tool_use", "tool_call"}:
                    return block
    return None


async def useMessageActions(*args: Any, **kwargs: Any) -> Any:
    message = option(args, kwargs, "message", scalar_arg(args, first_options(args)))
    return component_payload("message_actions", canCopy=bool(await copyTextOf(message)), toolCall=await toolCallOf(message), navigable=await isNavigableMessage(message))


async def useSelectedMessageBg(*args: Any, **kwargs: Any) -> Any:
    selected = bool(option(args, kwargs, "selected", scalar_arg(args, False)))
    return "selected" if selected else "normal"


__all__ = [
    "InVirtualListContext",
    "MESSAGE_ACTIONS",
    "MessageActionsSelectedContext",
    "MessageActionsBar",
    "MessageActionsKeybindings",
    "copyTextOf",
    "isNavigableMessage",
    "stripSystemReminders",
    "toolCallOf",
    "useMessageActions",
    "useSelectedMessageBg",
]
