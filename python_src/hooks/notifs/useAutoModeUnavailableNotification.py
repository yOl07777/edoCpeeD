from __future__ import annotations

from typing import Any

from ._notification import first_mapping, notification, pick, truthy


async def useAutoModeUnavailableNotification(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    unavailable = truthy(pick(options, "unavailable", "disabled", default=False))
    reason = str(pick(options, "reason", default="Auto mode is not available for this workspace."))
    return notification(visible=unavailable, level="warning", title="Auto mode unavailable", message=reason)
