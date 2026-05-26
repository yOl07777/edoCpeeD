from __future__ import annotations

from typing import Any

from ._notification import first_mapping, notification, pick


async def usePluginInstallationStatus(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    plugin = str(pick(options, "plugin", "name", default="plugin"))
    status = str(pick(options, "status", default="idle"))
    level = "success" if status in {"installed", "success"} else "error" if status in {"failed", "error"} else "info"
    return notification(
        visible=status != "idle",
        level=level,
        title="Plugin installation",
        message=f"{plugin}: {status}",
        plugin=plugin,
        status=status,
    )
