from __future__ import annotations

from typing import Any

from python_src.commands.plugin._shared import command_result, list_plugins


async def filterManagedDisabledPlugins(plugins: list[dict[str, Any]] | dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> list[Any]:
    if isinstance(plugins, dict):
        iterable = plugins.values()
    else:
        iterable = plugins or []
    return [plugin for plugin in iterable if isinstance(plugin, dict) and not plugin.get("enabled", True)]


async def ManagePlugins(*args: Any, **kwargs: Any) -> dict[str, Any]:
    plugins = await list_plugins()
    return command_result(
        f"Installed plugins: {len(plugins['items'])}.",
        plugins=plugins["items"],
        disabled=await filterManagedDisabledPlugins(plugins["items"]),
        path=plugins.get("path"),
    )


__all__ = ["ManagePlugins", "filterManagedDisabledPlugins"]
