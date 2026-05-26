from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload


async def CollapsedReadSearchContent(*args: Any, **kwargs: Any) -> Any:
    items = kwargs.get("items") or kwargs.get("results") or (args[0] if args else []) or []
    if isinstance(items, str):
        items = items.splitlines()
    return message_payload("collapsed_read_search_content", count=len(items), preview=[str(item) for item in list(items)[:5]])


__all__ = ["CollapsedReadSearchContent"]
