from __future__ import annotations

from typing import Any


async def FlashingChar(char: str = "*", *_args: Any, **kwargs: Any) -> dict[str, Any]:
    frame = int(kwargs.get("frame", 0) or 0)
    return {"type": "flashing_char", "provider": "deepseek", "char": char, "visible": frame % 2 == 0}


__all__ = ["FlashingChar"]
