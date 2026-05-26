from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload, text_from


async def AssistantThinkingMessage(*args: Any, **kwargs: Any) -> Any:
    text = text_from(args[0] if args else None, **kwargs)
    return message_payload("assistant_thinking_message", role="assistant", text=text, redacted=bool(kwargs.get("redacted", False)))


__all__ = ["AssistantThinkingMessage"]
