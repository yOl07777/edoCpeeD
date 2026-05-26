from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload, text_from


async def UserChannelMessage(*args: Any, **kwargs: Any) -> Any:
    return message_payload("user_channel_message", channel=str(kwargs.get("channel") or "default"), text=text_from(args[0] if args else None, **kwargs))


__all__ = ["UserChannelMessage"]
