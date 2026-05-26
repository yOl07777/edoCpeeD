"""User keybinding configuration loader."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable

from .defaultBindings import DEFAULT_BINDINGS
from .parser import parseBindings
from .validate import validateBindings

_cached_bindings: list[dict[str, Any]] | None = None
_cached_warnings: list[dict[str, Any]] = []
_subscribers: list[Callable[[dict[str, Any]], Any]] = []
_initialized = False


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _config_home() -> Path:
    return Path(os.getenv("DEEPCODE_CONFIG_HOME") or os.getenv("CLAUDE_CONFIG_DIR") or Path.home() / ".deepcode")


def isKeybindingCustomizationEnabled() -> bool:
    return _truthy(os.getenv("DEEPSEEK_KEYBINDINGS_ENABLED") or os.getenv("TENGU_KEYBINDING_CUSTOMIZATION_RELEASE"))


def getKeybindingsPath() -> str:
    return str(_config_home() / "keybindings.json")


def _parse_bindings(blocks: Any) -> list[dict[str, Any]]:
    if not isinstance(blocks, list):
        raise ValueError('"bindings" must be an array')
    warnings = validateBindings(blocks)
    if any(warning.get("severity") == "error" for warning in warnings):
        raise ValueError("; ".join(str(warning.get("message")) for warning in warnings if warning.get("severity") == "error"))
    return parseBindings(blocks)


def _default_bindings() -> list[dict[str, Any]]:
    return parseBindings(DEFAULT_BINDINGS)


async def loadKeybindings() -> dict[str, Any]:
    return loadKeybindingsSyncWithWarnings()


def loadKeybindingsSync() -> list[dict[str, Any]]:
    return loadKeybindingsSyncWithWarnings()["bindings"]


def loadKeybindingsSyncWithWarnings() -> dict[str, Any]:
    global _cached_bindings, _cached_warnings
    if _cached_bindings is not None:
        return {"bindings": list(_cached_bindings), "warnings": list(_cached_warnings)}
    defaults = _default_bindings()
    if not isKeybindingCustomizationEnabled():
        _cached_bindings = defaults
        _cached_warnings = []
        return {"bindings": list(defaults), "warnings": []}
    path = Path(getKeybindingsPath())
    if not path.exists():
        _cached_bindings = defaults
        _cached_warnings = []
        return {"bindings": list(defaults), "warnings": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "bindings" not in data:
            raise ValueError('keybindings.json must have a "bindings" array')
        warnings = validateBindings(data["bindings"])
        user = parseBindings(data["bindings"]) if isinstance(data["bindings"], list) else []
        _cached_bindings = defaults + user
        _cached_warnings = warnings
    except Exception as exc:
        _cached_bindings = defaults
        _cached_warnings = [{"type": "parse_error", "severity": "error", "message": str(exc)}]
    return {"bindings": list(_cached_bindings), "warnings": list(_cached_warnings)}


async def initializeKeybindingWatcher() -> None:
    global _initialized
    _initialized = True


def disposeKeybindingWatcher() -> None:
    global _initialized
    _initialized = False
    _subscribers.clear()


def subscribeToKeybindingChanges(callback: Callable[[dict[str, Any]], Any]) -> Callable[[], None]:
    _subscribers.append(callback)

    def unsubscribe() -> None:
        if callback in _subscribers:
            _subscribers.remove(callback)

    return unsubscribe


def getCachedKeybindingWarnings() -> list[dict[str, Any]]:
    return list(_cached_warnings)


def resetKeybindingLoaderForTesting() -> None:
    global _cached_bindings, _cached_warnings, _initialized
    _cached_bindings = None
    _cached_warnings = []
    _initialized = False
    _subscribers.clear()
