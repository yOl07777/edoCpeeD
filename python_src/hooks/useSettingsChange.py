from __future__ import annotations

from typing import Any

from ._basic import first_mapping, pick


async def useSettingsChange(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    previous = pick(options, "previous", "old", default={}) or {}
    current = pick(options, "current", "new", default={}) or {}
    keys = sorted(set(previous) | set(current)) if isinstance(previous, dict) and isinstance(current, dict) else []
    changed = [key for key in keys if previous.get(key) != current.get(key)]
    return {"provider": "deepseek", "changed": changed, "hasChanges": bool(changed), "previous": previous, "current": current}
