from __future__ import annotations

import os
from typing import Any

from ._shared import get_global_config, mutate_global_config, update_user_settings, user_settings


async def migrateAutoUpdatesToSettings(*_args: Any, **_kwargs: Any) -> bool:
    """Move explicit auto-update opt-out from global config to user settings."""

    config = await get_global_config()
    if config.get("autoUpdates") is not False or config.get("autoUpdatesProtectedForNative") is True:
        return False
    settings = await user_settings()
    env = dict(settings.get("env") or {})
    env["DISABLE_AUTOUPDATER"] = "1"
    await update_user_settings({"env": env})
    os.environ["DISABLE_AUTOUPDATER"] = "1"

    def remove_keys(current: dict[str, Any]) -> dict[str, Any]:
        next_config = dict(current)
        next_config.pop("autoUpdates", None)
        next_config.pop("autoUpdatesProtectedForNative", None)
        return next_config

    await mutate_global_config(remove_keys)
    return True
