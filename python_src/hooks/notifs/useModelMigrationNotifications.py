from __future__ import annotations

from typing import Any

from ._notification import first_mapping, notification, pick


async def useModelMigrationNotifications(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    old_model = str(pick(options, "oldModel", "fromModel", default=""))
    new_model = str(pick(options, "newModel", "toModel", default=pick(options, "model", default="deepseek-chat")))
    visible = bool(old_model and old_model != new_model)
    return notification(
        visible=visible,
        title="Model migrated",
        message=f"Model setting was migrated from {old_model} to {new_model}.",
        oldModel=old_model,
        newModel=new_model,
    )
