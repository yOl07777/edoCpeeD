"""Built-in plugin initialization shim.

The upstream TS module currently registers no bundled plugins. This Python
version keeps the startup hook importable and returns a small status payload so
tests and callers can confirm initialization ran.
"""

from __future__ import annotations

from typing import Any

_initialized = False
_registered_plugins: list[dict[str, Any]] = []


def initBuiltinPlugins() -> dict[str, Any]:
    global _initialized
    _initialized = True
    return {"initialized": True, "count": len(_registered_plugins), "plugins": list(_registered_plugins)}


def getBuiltinPlugins() -> list[dict[str, Any]]:
    return list(_registered_plugins)


def isInitialized() -> bool:
    return _initialized


__all__ = ["getBuiltinPlugins", "initBuiltinPlugins", "isInitialized"]
