"""Leaf cache state for remote managed settings."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

SETTINGS_FILENAME = "remote-settings.json"

_session_cache: dict[str, Any] | None = None
_eligible: bool | None = None


def _config_home() -> Path:
    root = os.getenv("DEEPCODE_CONFIG_HOME") or os.getenv("DEEPSEEK_CODE_HOME")
    return Path(root).expanduser().resolve() if root else (Path.home() / ".deepcode").resolve()


async def getSettingsPath(*args: Any, **kwargs: Any) -> str:
    return str(_config_home() / SETTINGS_FILENAME)


async def setSessionCache(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    global _session_cache
    value = kwargs.get("value") if "value" in kwargs else (args[0] if args else None)
    _session_cache = dict(value) if isinstance(value, dict) else None
    return _session_cache


async def setEligibility(*args: Any, **kwargs: Any) -> bool:
    global _eligible
    value = bool(kwargs.get("value") if "value" in kwargs else (args[0] if args else False))
    _eligible = value
    return value


async def resetSyncCache(*args: Any, **kwargs: Any) -> None:
    global _session_cache, _eligible
    _session_cache = None
    _eligible = None


def _load_settings_sync() -> dict[str, Any] | None:
    try:
        path = _config_home() / SETTINGS_FILENAME
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


async def getRemoteManagedSettingsSyncFromCache(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    global _session_cache
    if _eligible is not True:
        return None
    if _session_cache is not None:
        return dict(_session_cache)
    cached = _load_settings_sync()
    if cached is not None:
        _session_cache = cached
        return dict(cached)
    return None


__all__ = [
    "getRemoteManagedSettingsSyncFromCache",
    "getSettingsPath",
    "resetSyncCache",
    "setEligibility",
    "setSessionCache",
]
