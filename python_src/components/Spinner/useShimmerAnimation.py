from __future__ import annotations

from typing import Any


async def useShimmerAnimation(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    frame = int(kwargs.get("frame", 0) or 0)
    width = int(kwargs.get("width", 8) or 8)
    return {"type": "shimmer_animation", "provider": "deepseek", "frame": frame, "position": frame % max(1, width)}


__all__ = ["useShimmerAnimation"]
