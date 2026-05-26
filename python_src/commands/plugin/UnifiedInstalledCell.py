from __future__ import annotations

from typing import Any

from python_src.commands.plugin._shared import plugin_summary


async def UnifiedInstalledCell(plugin: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    plugin = plugin or kwargs.get("plugin") or {}
    name = str(plugin.get("name") or kwargs.get("name") or "unknown")
    return {"type": "plugin_cell", "plugin": plugin_summary(name, plugin)}


__all__ = ["UnifiedInstalledCell"]
