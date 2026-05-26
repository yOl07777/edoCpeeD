from __future__ import annotations

from typing import Any

from python_src.components.LogoV2._shared import logo_payload, normalize_feed_items, option


async def Feed(*args: Any, **kwargs: Any) -> Any:
    items = option(args, kwargs, "items", args[0] if args else None)
    rows = normalize_feed_items(items)
    width = await calculateFeedWidth(rows)
    return logo_payload("logo_feed", items=rows, count=len(rows), width=width)


async def calculateFeedWidth(*args: Any, **kwargs: Any) -> Any:
    items = args[0] if args else kwargs.get("items")
    rows = normalize_feed_items(items)
    minimum = int(kwargs.get("minimum", 16))
    maximum = int(kwargs.get("maximum", 80))
    width = max([len(row["text"]) for row in rows] + [minimum])
    return min(width, maximum)


__all__ = ["Feed", "calculateFeedWidth"]
