from __future__ import annotations

from typing import Any

from python_src.plugins.plugin_store import discover_plugins
from python_src.tools.base import PythonTool, object_schema


async def reload_plugins(root: str = ".", *, cwd: str | None = None) -> dict[str, Any]:
    plugins = discover_plugins(root, cwd=cwd)
    return {"reloaded": len(plugins), "plugins": plugins}


call = PythonTool(
    name="reload_plugins",
    description="Rediscover local plugin manifests.",
    parameters=object_schema({"root": {"type": "string", "default": "."}}),
    handler=reload_plugins,
    read_only=True,
)
