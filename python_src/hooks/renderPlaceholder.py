from __future__ import annotations

from typing import Any


async def renderPlaceholder(value: Any = "", *_args: Any, **kwargs: Any) -> str:
    text = str(kwargs.get("placeholder", value) or "")
    focused = bool(kwargs.get("focused", True))
    if not text:
        return ""
    return text if focused else f"({text})"


__all__ = ["renderPlaceholder"]
