from __future__ import annotations

from typing import Any


BUILTIN_MARKETPLACE_NAME = "builtin"
_BUILTIN_PLUGINS: dict[str, dict[str, Any]] = {}


def registerBuiltinPlugin(plugin_id: str, definition: dict[str, Any]) -> dict[str, Any]:
    _BUILTIN_PLUGINS[plugin_id] = {"id": plugin_id, **definition}
    return _BUILTIN_PLUGINS[plugin_id]


def clearBuiltinPlugins() -> None:
    _BUILTIN_PLUGINS.clear()


def getBuiltinPlugins() -> list[dict[str, Any]]:
    return list(_BUILTIN_PLUGINS.values())


def getBuiltinPluginDefinition(plugin_id: str) -> dict[str, Any] | None:
    return _BUILTIN_PLUGINS.get(plugin_id)


def isBuiltinPluginId(plugin_id: str) -> bool:
    return plugin_id in _BUILTIN_PLUGINS


def getBuiltinPluginSkillCommands(plugin_id: str) -> list[dict[str, Any]]:
    plugin = getBuiltinPluginDefinition(plugin_id) or {}
    return list(plugin.get("skill_commands", []))
