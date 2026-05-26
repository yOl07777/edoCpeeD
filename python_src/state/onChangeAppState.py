"""AppState change hooks migrated for the Python runtime."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


_EXTERNAL_MODE_ALIASES = {
    "default": "default",
    "acceptEdits": "acceptEdits",
    "plan": "plan",
    "bypassPermissions": "bypassPermissions",
    "auto": "default",
    "bubble": "default",
}


def _mode_from_external(value: str) -> str:
    return _EXTERNAL_MODE_ALIASES.get(value, value)


def _to_external_mode(value: str | None) -> str | None:
    if value is None:
        return None
    return _EXTERNAL_MODE_ALIASES.get(value, value)


def externalMetadataToAppState(metadata: dict[str, Any]) -> Any:
    """Return an updater that restores session metadata into AppState."""

    def updater(prev: dict[str, Any]) -> dict[str, Any]:
        next_state = deepcopy(prev)
        permission_mode = metadata.get("permission_mode")
        if isinstance(permission_mode, str):
            context = dict(next_state.get("toolPermissionContext") or {})
            context["mode"] = _mode_from_external(permission_mode)
            next_state["toolPermissionContext"] = context
        if isinstance(metadata.get("is_ultraplan_mode"), bool):
            next_state["isUltraplanMode"] = metadata["is_ultraplan_mode"]
        return next_state

    return updater


def onChangeAppState(args: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    """Describe side effects that the TS hook would notify or persist.

    The JS implementation talks to CCR/session streams and writes global
    settings.  The Python migration keeps this deterministic and side-effect
    light: callers receive the same change information and can decide where to
    persist it.
    """

    payload = args or kwargs
    new_state = payload.get("newState") or {}
    old_state = payload.get("oldState") or {}
    changes: list[str] = []
    metadata: dict[str, Any] = {}
    settings_update: dict[str, Any] = {}
    global_config_update: dict[str, Any] = {}

    old_context = old_state.get("toolPermissionContext") or {}
    new_context = new_state.get("toolPermissionContext") or {}
    old_mode = old_context.get("mode")
    new_mode = new_context.get("mode")
    if old_mode != new_mode:
        changes.append("permission_mode")
        old_external = _to_external_mode(old_mode)
        new_external = _to_external_mode(new_mode)
        if old_external != new_external:
            metadata["permission_mode"] = new_external
            metadata["is_ultraplan_mode"] = (
                True
                if new_external == "plan"
                and new_state.get("isUltraplanMode")
                and not old_state.get("isUltraplanMode")
                else None
            )

    if new_state.get("mainLoopModel") != old_state.get("mainLoopModel"):
        changes.append("mainLoopModel")
        settings_update["model"] = new_state.get("mainLoopModel")

    if new_state.get("expandedView") != old_state.get("expandedView"):
        changes.append("expandedView")
        global_config_update["showExpandedTodos"] = new_state.get("expandedView") == "tasks"
        global_config_update["showSpinnerTree"] = new_state.get("expandedView") == "teammates"

    if new_state.get("verbose") != old_state.get("verbose"):
        changes.append("verbose")
        global_config_update["verbose"] = bool(new_state.get("verbose"))

    if new_state.get("settings") != old_state.get("settings"):
        changes.append("settings")
        if (new_state.get("settings") or {}).get("env") != (old_state.get("settings") or {}).get("env"):
            changes.append("settings.env")

    return {
        "changes": changes,
        "metadata": metadata,
        "settingsUpdate": settings_update,
        "globalConfigUpdate": global_config_update,
    }


__all__ = ["externalMetadataToAppState", "onChangeAppState"]
