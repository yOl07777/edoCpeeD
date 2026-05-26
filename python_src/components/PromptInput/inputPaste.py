from __future__ import annotations

from typing import Any

from python_src.components.PromptInput._shared import truncate_text


async def maybeTruncateInput(*args: Any, **kwargs: Any) -> Any:
    text = str(kwargs.get("input") or (args[0] if args else "") or "")
    return truncate_text(text, int(kwargs.get("limit", 20000) or 20000))


async def maybeTruncateMessageForInput(*args: Any, **kwargs: Any) -> Any:
    message = kwargs.get("message") if "message" in kwargs else (args[0] if args else "")
    text = message.get("content", "") if isinstance(message, dict) else str(message)
    return await maybeTruncateInput(text, limit=kwargs.get("limit", 20000))


__all__ = ["maybeTruncateInput", "maybeTruncateMessageForInput"]
