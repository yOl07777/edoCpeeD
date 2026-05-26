from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload, text_from


async def UserPromptMessage(*args: Any, **kwargs: Any) -> Any:
    text = text_from(args[0] if args else None, **kwargs)
    return message_payload("user_prompt_message", role="user", text=text, prompt=True)


__all__ = ["UserPromptMessage"]
