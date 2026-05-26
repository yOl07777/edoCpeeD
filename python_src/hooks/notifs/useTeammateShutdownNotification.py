from __future__ import annotations

from typing import Any

from ._notification import first_mapping, notification, pick


async def useTeammateLifecycleNotification(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    name = str(pick(options, "name", "teammate", default="teammate"))
    event = str(pick(options, "event", "status", default="shutdown"))
    level = "warning" if event in {"shutdown", "stopped", "failed"} else "info"
    return notification(
        visible=True,
        level=level,
        title="Teammate lifecycle",
        message=f"{name}: {event}",
        name=name,
        event=event,
    )
