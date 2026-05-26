from __future__ import annotations

from typing import Any

from ._basic import first_mapping, listify, pick


async def useVirtualScroll(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    items = listify(pick(options, "items", default=[]))
    offset = max(0, int(pick(options, "offset", default=0)))
    height = max(0, int(pick(options, "height", "window", default=10)))
    visible = items[offset : offset + height]
    return {"provider": "deepseek", "offset": offset, "height": height, "visible": visible, "total": len(items)}
