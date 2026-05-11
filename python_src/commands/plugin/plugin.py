from __future__ import annotations

from typing import Any

from python_src.plugins.builtinPlugins import getBuiltinPlugins, registerBuiltinPlugin
from python_src.plugins.plugin_store import discover_plugins
from python_src.tools.base import PythonTool, object_schema


async def plugin_command(
    action: str,
    *,
    root: str = ".",
    plugin_id: str | None = None,
    definition: dict[str, Any] | None = None,
    cwd: str | None = None,
) -> dict[str, Any]:
    if action == "discover":
        plugins = discover_plugins(root, cwd=cwd)
        return {"count": len(plugins), "plugins": plugins}
    if action == "list_builtin":
        plugins = getBuiltinPlugins()
        return {"count": len(plugins), "plugins": plugins}
    if action == "register_builtin":
        if not plugin_id:
            raise ValueError("plugin_id is required")
        return registerBuiltinPlugin(plugin_id, definition or {})
    raise ValueError(f"Unknown plugin action: {action}")


call = PythonTool(
    name="plugin",
    description="Discover local plugins or manage lightweight builtin plugin definitions.",
    parameters=object_schema(
        {
            "action": {"type": "string", "enum": ["discover", "list_builtin", "register_builtin"]},
            "root": {"type": "string", "default": "."},
            "plugin_id": {"type": "string"},
            "definition": {"type": "object"},
        },
        required=["action"],
    ),
    handler=plugin_command,
    read_only=False,
)
