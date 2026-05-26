from __future__ import annotations

from typing import Any

from ._notification import first_mapping, notification, pick


async def useStartupNotification(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    model = str(pick(options, "model", default="deepseek-chat"))
    workspace = str(pick(options, "workspace", default="current workspace"))
    return notification(
        visible=bool(pick(options, "visible", default=True)),
        title="DeepSeek Code ready",
        message=f"Using {model} in {workspace}.",
        model=model,
        workspace=workspace,
    )
