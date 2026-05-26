from __future__ import annotations

from typing import Any


async def Passes(*args: Any, **kwargs: Any) -> Any:
    passes = kwargs.get("passes") or (args[0] if args else []) or []
    if isinstance(passes, dict):
        rows = [{"name": key, "remaining": value} for key, value in passes.items()]
    else:
        rows = [item if isinstance(item, dict) else {"name": str(item), "remaining": None} for item in passes]
    return {"type": "passes", "provider": "deepseek", "passes": rows, "count": len(rows)}


__all__ = ["Passes"]
