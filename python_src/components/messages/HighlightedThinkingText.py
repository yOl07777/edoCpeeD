from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload, text_from


async def HighlightedThinkingText(*args: Any, **kwargs: Any) -> Any:
    text = text_from(args[0] if args else None, **kwargs)
    return message_payload("highlighted_thinking_text", text=text, highlighted=bool(text.strip()))


__all__ = ["HighlightedThinkingText"]
