from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload, text_from


async def UserMemoryInputMessage(*args: Any, **kwargs: Any) -> Any:
    text = text_from(args[0] if args else None, **kwargs)
    return message_payload("user_memory_input_message", text=text, target=kwargs.get("target", ".deepseek/memory.md"))


__all__ = ["UserMemoryInputMessage"]
