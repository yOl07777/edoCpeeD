from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload, text_from


async def TeammateMessageContent(*args: Any, **kwargs: Any) -> Any:
    return text_from(args[0] if args else None, **kwargs)


async def UserTeammateMessage(*args: Any, **kwargs: Any) -> Any:
    text = await TeammateMessageContent(args[0] if args else None, **kwargs)
    teammate = str(kwargs.get("teammate") or kwargs.get("agent") or "teammate")
    return message_payload("user_teammate_message", teammate=teammate, text=text)


__all__ = ["TeammateMessageContent", "UserTeammateMessage"]
