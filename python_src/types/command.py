from __future__ import annotations

from typing import Any


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def getCommandName(cmd: Any) -> str:
    user_facing = _get(cmd, "userFacingName")
    if callable(user_facing):
        return str(user_facing())
    return str(_get(cmd, "name", ""))


def isCommandEnabled(cmd: Any) -> bool:
    is_enabled = _get(cmd, "isEnabled")
    if callable(is_enabled):
        return bool(is_enabled())
    if is_enabled is None:
        return True
    return bool(is_enabled)


__all__ = ["getCommandName", "isCommandEnabled"]
