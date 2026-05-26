from __future__ import annotations

from typing import Any

from python_src.components.LogoV2._shared import logo_payload, normalize_feed_items, option


async def FeedColumn(*args: Any, **kwargs: Any) -> Any:
    items = normalize_feed_items(option(args, kwargs, "items", args[0] if args else None))
    title = str(option(args, kwargs, "title", "Activity"))
    return logo_payload("feed_column", title=title, rows=items, count=len(items))


__all__ = ["FeedColumn"]
