from __future__ import annotations

from typing import Any


async def RecentDenialsTab(*args: Any, **kwargs: Any) -> dict[str, Any]:
    denials = kwargs.get("denials") or kwargs.get("items") or (args[0] if args else []) or []
    return {"type": "recent_denials_tab", "provider": "deepseek", "denials": list(denials), "count": len(denials)}


__all__ = ["RecentDenialsTab"]
