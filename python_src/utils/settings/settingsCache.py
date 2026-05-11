from __future__ import annotations

from typing import Any


_SESSION_SETTINGS_CACHE: dict[str, Any] = {}
_PARSED_FILE_CACHE: dict[str, Any] = {}
_SETTINGS_BY_SOURCE_CACHE: dict[str, Any] = {}
_PLUGIN_SETTINGS_BASE: dict[str, Any] = {}


async def resetSettingsCache() -> None:
    _SESSION_SETTINGS_CACHE.clear()
    _PARSED_FILE_CACHE.clear()
    _SETTINGS_BY_SOURCE_CACHE.clear()
    _PLUGIN_SETTINGS_BASE.clear()


async def getSessionSettingsCache() -> dict[str, Any]:
    return dict(_SESSION_SETTINGS_CACHE)


async def setSessionSettingsCache(value: dict[str, Any]) -> dict[str, Any]:
    _SESSION_SETTINGS_CACHE.clear()
    _SESSION_SETTINGS_CACHE.update(value)
    return dict(_SESSION_SETTINGS_CACHE)


async def getCachedParsedFile(path: str) -> Any:
    return _PARSED_FILE_CACHE.get(path)


async def setCachedParsedFile(path: str, value: Any) -> Any:
    _PARSED_FILE_CACHE[path] = value
    return value


async def getCachedSettingsForSource(source: str) -> Any:
    return _SETTINGS_BY_SOURCE_CACHE.get(source)


async def setCachedSettingsForSource(source: str, value: Any) -> Any:
    _SETTINGS_BY_SOURCE_CACHE[source] = value
    return value


async def getPluginSettingsBase() -> dict[str, Any]:
    return dict(_PLUGIN_SETTINGS_BASE)


async def setPluginSettingsBase(value: dict[str, Any]) -> dict[str, Any]:
    _PLUGIN_SETTINGS_BASE.clear()
    _PLUGIN_SETTINGS_BASE.update(value)
    return dict(_PLUGIN_SETTINGS_BASE)


async def clearPluginSettingsBase() -> None:
    _PLUGIN_SETTINGS_BASE.clear()
