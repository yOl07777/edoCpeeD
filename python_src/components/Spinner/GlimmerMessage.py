from __future__ import annotations

from typing import Any


async def GlimmerMessage(message: str = "Thinking", *_args: Any, **kwargs: Any) -> dict[str, Any]:
    frame = int(kwargs.get("frame", 0) or 0)
    dots = "." * (frame % 4)
    return {"type": "glimmer_message", "provider": "deepseek", "text": f"{message}{dots}"}


__all__ = ["GlimmerMessage"]
