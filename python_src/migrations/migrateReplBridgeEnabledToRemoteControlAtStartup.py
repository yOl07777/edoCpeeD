from __future__ import annotations

from typing import Any

from ._shared import mutate_global_config


async def migrateReplBridgeEnabledToRemoteControlAtStartup(*_args: Any, **_kwargs: Any) -> bool:
    """Rename legacy replBridgeEnabled config to remoteControlAtStartup."""

    changed = False

    def migrate(current: dict[str, Any]) -> dict[str, Any]:
        nonlocal changed
        if "replBridgeEnabled" not in current or current.get("remoteControlAtStartup") is not None:
            return current
        next_config = dict(current)
        next_config["remoteControlAtStartup"] = bool(next_config.pop("replBridgeEnabled"))
        changed = True
        return next_config

    await mutate_global_config(migrate)
    return changed
