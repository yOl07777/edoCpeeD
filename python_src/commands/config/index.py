from __future__ import annotations

import os
from typing import Any

from python_src.utils.settings.applySettingsChange import applySettingsChange
from python_src.utils.settings.settings import getInitialSettings, getSettingsWithSources


async def config_command(
    action: str = "list",
    *,
    key: str | None = None,
    value: Any = None,
    source: str = "project",
    cwd: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    if action == "list":
        return await getSettingsWithSources(cwd)
    if action == "get":
        if not key:
            raise ValueError("key is required for config get")
        return {"key": key, "value": (await getInitialSettings(cwd)).get(key)}
    if action in {"set", "delete", "append"}:
        if not key:
            raise ValueError("key is required for config change")
        return await applySettingsChange(key, value, action=action, source=source, cwd=cwd)
    raise ValueError(f"Unsupported config action: {action}")


call = config_command
