from __future__ import annotations

from typing import Any

from ._notification import first_mapping, notification, pick, truthy


async def useFastModeNotification(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    enabled = truthy(pick(options, "enabled", "fastMode", default=False))
    model = str(pick(options, "model", default="deepseek-chat"))
    return notification(
        visible=enabled,
        title="Fast mode enabled",
        message=f"DeepSeek Code is using {model} for faster responses.",
        model=model,
    )
