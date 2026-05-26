from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload, text_from


async def UserTextMessage(*args: Any, **kwargs: Any) -> Any:
    text = text_from(args[0] if args else None, **kwargs)
    return message_payload("user_text_message", role="user", text=text, length=len(text))


__all__ = ["UserTextMessage"]
