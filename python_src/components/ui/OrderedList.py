from __future__ import annotations

from typing import Any


async def OrderedList(*args: Any, **kwargs: Any) -> Any:
    items = kwargs.get("items") or (args[0] if args else []) or []
    return {"type": "ordered_list", "provider": "deepseek", "items": [{"number": index + 1, "text": str(item)} for index, item in enumerate(items)], "count": len(items)}


__all__ = ["OrderedList"]
