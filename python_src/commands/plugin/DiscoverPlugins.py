from __future__ import annotations

from typing import Any

from python_src.plugins.plugin_store import discover_plugins
from python_src.commands.plugin._shared import command_result


async def DiscoverPlugins(*args: Any, **kwargs: Any) -> dict[str, Any]:
    root = kwargs.get("root") or (args[0] if args else ".")
    cwd = kwargs.get("cwd")
    plugins = discover_plugins(str(root), cwd=cwd)
    return command_result(f"Discovered {len(plugins)} plugin(s).", plugins=plugins)


__all__ = ["DiscoverPlugins"]
