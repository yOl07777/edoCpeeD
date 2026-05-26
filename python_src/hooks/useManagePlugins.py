from __future__ import annotations

from typing import Any


async def useManagePlugins(plugins: list[dict[str, Any]] | None = None, *_args: Any, **kwargs: Any) -> dict[str, Any]:
    rows = list(kwargs.get("plugins", plugins or []))
    enabled = [plugin for plugin in rows if plugin.get("enabled", True)]
    return {"provider": "deepseek", "plugins": rows, "count": len(rows), "enabledCount": len(enabled)}


__all__ = ["useManagePlugins"]
