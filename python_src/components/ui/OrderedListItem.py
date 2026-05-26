from __future__ import annotations

from typing import Any


OrderedListItemContext: dict[str, Any] = {"provider": "deepseek"}


async def OrderedListItem(*args: Any, **kwargs: Any) -> Any:
    text = str(kwargs.get("text") or (args[0] if args else ""))
    number = int(kwargs.get("number", args[1] if len(args) > 1 else 1) or 1)
    return {"type": "ordered_list_item", "provider": "deepseek", "number": number, "text": text}


__all__ = ["OrderedListItem", "OrderedListItemContext"]
