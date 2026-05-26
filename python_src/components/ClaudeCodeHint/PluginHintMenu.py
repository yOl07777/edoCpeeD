from __future__ import annotations

from typing import Any


async def PluginHintMenu(*args: Any, **kwargs: Any) -> Any:
    plugins = kwargs.get("plugins") or (args[0] if args else []) or []
    query = str(kwargs.get("query") or "").lower()
    rows = []
    for plugin in plugins:
        if isinstance(plugin, dict):
            name = str(plugin.get("name") or plugin.get("id") or "")
            description = str(plugin.get("description") or "")
        else:
            name = str(plugin)
            description = ""
        if not query or query in name.lower() or query in description.lower():
            rows.append({"name": name, "description": description, "enabled": bool(plugin.get("enabled", True)) if isinstance(plugin, dict) else True})
    return {
        "type": "plugin_hint_menu",
        "provider": "deepseek",
        "title": "DeepSeek Code plugins",
        "plugins": rows,
        "count": len(rows),
    }


__all__ = ["PluginHintMenu"]
