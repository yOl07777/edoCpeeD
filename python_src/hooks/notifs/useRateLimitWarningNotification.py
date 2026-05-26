from __future__ import annotations

from typing import Any

from ._notification import first_mapping, notification, pick


async def useRateLimitWarningNotification(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    remaining = pick(options, "remaining", default=None)
    reset = pick(options, "resetAt", "reset", default=None)
    visible = remaining is not None and int(remaining) <= int(pick(options, "threshold", default=5))
    message = f"DeepSeek rate limit is low ({remaining} remaining)."
    if reset:
        message += f" Reset: {reset}."
    return notification(visible=visible, level="warning", title="Rate limit warning", message=message, remaining=remaining, resetAt=reset)
