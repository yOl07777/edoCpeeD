from __future__ import annotations

from typing import Any

from ._basic import first_mapping, listify, pick


async def useQueueProcessor(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    queue = listify(pick(options, "queue", "items", default=[]))
    limit = int(pick(options, "limit", "maxItems", default=len(queue) or 0))
    processed = queue[:limit] if limit >= 0 else queue
    return {
        "provider": "deepseek",
        "processed": processed,
        "remaining": queue[len(processed) :],
        "processedCount": len(processed),
        "idle": not queue,
    }
