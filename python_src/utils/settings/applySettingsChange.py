from __future__ import annotations

import os
from typing import Any

from python_src.utils.settings.settings import getSettingsForSource, updateSettingsForSource


async def applySettingsChange(
    key: str,
    value: Any = None,
    *,
    action: str = "set",
    source: str = "project",
    cwd: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    current = (await getSettingsForSource(source, cwd)).get("settings", {})
    updated = dict(current)
    if action == "delete":
        updated.pop(key, None)
    elif action == "append":
        existing = updated.get(key, [])
        if not isinstance(existing, list):
            existing = [existing]
        existing.append(value)
        updated[key] = existing
    else:
        updated[key] = value
    return await updateSettingsForSource(source, updated, cwd=cwd)
