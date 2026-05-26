from __future__ import annotations

from typing import Any

from ._notification import first_mapping, notification, pick, truthy


async def useIDEStatusIndicator(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    connected = truthy(pick(options, "connected", "ready", default=False))
    ide = str(pick(options, "ide", "name", default="IDE"))
    return notification(
        visible=True,
        level="success" if connected else "warning",
        title="IDE connection",
        message=f"{ide} is {'connected' if connected else 'not connected'}.",
        connected=connected,
        ide=ide,
    )
