from __future__ import annotations

from typing import Any


async def ShimmerChar(char: str = "-", *_args: Any, **kwargs: Any) -> dict[str, Any]:
    frame = int(kwargs.get("frame", 0) or 0)
    return {"type": "shimmer_char", "provider": "deepseek", "char": char, "phase": frame % 8}


__all__ = ["ShimmerChar"]
