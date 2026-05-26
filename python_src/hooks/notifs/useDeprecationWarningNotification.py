from __future__ import annotations

from typing import Any

from ._notification import first_mapping, notification, pick


async def useDeprecationWarningNotification(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    feature = str(pick(options, "feature", "name", default="This feature"))
    replacement = str(pick(options, "replacement", default="the DeepSeek-native workflow"))
    visible = bool(pick(options, "deprecated", default=feature != "This feature"))
    return notification(
        visible=visible,
        level="warning",
        title="Deprecated feature",
        message=f"{feature} is deprecated. Use {replacement} instead.",
        feature=feature,
        replacement=replacement,
    )
