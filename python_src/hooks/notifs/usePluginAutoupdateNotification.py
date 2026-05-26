from __future__ import annotations

from typing import Any

from ._notification import first_mapping, notification, pick


async def usePluginAutoupdateNotification(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    count = int(pick(options, "count", "updatedCount", default=0) or 0)
    return notification(
        visible=count > 0,
        title="Plugins updated",
        message=f"{count} plugin(s) were updated.",
        count=count,
    )
