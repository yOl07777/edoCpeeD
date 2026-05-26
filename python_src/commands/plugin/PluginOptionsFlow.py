from __future__ import annotations

from typing import Any

from python_src.commands.plugin._shared import command_result, list_plugins


async def findPluginOptionsTarget(name: str | None = None, *args: Any, **kwargs: Any) -> dict[str, Any] | None:
    target = name or kwargs.get("plugin") or (args[0] if args else None)
    plugins = await list_plugins()
    for plugin in plugins["items"]:
        if plugin.get("name") == target:
            return plugin
    return None


async def PluginOptionsFlow(*args: Any, **kwargs: Any) -> dict[str, Any]:
    target = await findPluginOptionsTarget(*args, **kwargs)
    if not target:
        return command_result("Plugin options target not found.", target=kwargs.get("plugin"))
    return command_result(f"Plugin options target: {target['name']}", plugin=target)


__all__ = ["PluginOptionsFlow", "findPluginOptionsTarget"]
