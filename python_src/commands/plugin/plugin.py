from __future__ import annotations

from typing import Any

from python_src.plugins.builtinPlugins import getBuiltinPlugins, registerBuiltinPlugin
from python_src.plugins.plugin_store import discover_plugins
from python_src.tools.base import PythonTool, object_schema
from python_src.cli.handlers import plugins as plugin_handlers
from python_src.commands.plugin._shared import PLUGIN_HELP, command_result, list_marketplaces, list_plugins
from python_src.commands.plugin.parseArgs import parsePluginArgs


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


async def local_call(onDone: Any | None = None, context: Any | None = None, args: str = "") -> dict[str, Any]:
    parsed = await parsePluginArgs(args)
    kind = parsed["type"]
    if kind in {"menu", "manage"}:
        plugins = await list_plugins()
        marketplaces = await list_marketplaces()
        value = f"Plugins: {len(plugins['items'])}; marketplaces: {len(marketplaces['items'])}."
        result = command_result(value, plugins=plugins["items"], marketplaces=marketplaces["items"], help=PLUGIN_HELP)
    elif kind == "help":
        result = command_result(PLUGIN_HELP, help=PLUGIN_HELP)
    elif kind == "install":
        plugin = parsed.get("plugin") or parsed.get("marketplace")
        if not plugin:
            result = command_result("Specify a plugin name or marketplace source.", parsed=parsed)
        else:
            installed = await plugin_handlers.pluginInstallHandler(plugin, {"source": parsed.get("marketplace") or plugin})
            result = command_result(f"Recorded plugin installation: {plugin}", result=installed)
    elif kind == "uninstall":
        plugin = parsed.get("plugin")
        result = command_result("Specify a plugin to uninstall.", parsed=parsed) if not plugin else command_result(
            f"Removed plugin: {plugin}",
            result=await plugin_handlers.pluginUninstallHandler(plugin, {}),
        )
    elif kind == "enable":
        plugin = parsed.get("plugin")
        result = command_result("Specify a plugin to enable.", parsed=parsed) if not plugin else command_result(
            f"Enabled plugin: {plugin}",
            result=await plugin_handlers.pluginEnableHandler(plugin, {}),
        )
    elif kind == "disable":
        plugin = parsed.get("plugin")
        result = command_result("Specify a plugin to disable.", parsed=parsed) if not plugin else command_result(
            f"Disabled plugin: {plugin}",
            result=await plugin_handlers.pluginDisableHandler(plugin, {}),
        )
    elif kind == "validate":
        path = parsed.get("path")
        result = command_result("Specify a plugin manifest path.", parsed=parsed) if not path else command_result(
            f"Validated plugin manifest: {path}",
            result=await plugin_handlers.pluginValidateHandler(path, {}),
        )
    elif kind == "marketplace":
        action = parsed.get("action")
        target = parsed.get("target")
        if action == "add" and target:
            result = command_result(f"Added marketplace: {target}", result=await plugin_handlers.marketplaceAddHandler(target, {}))
        elif action == "remove" and target:
            result = command_result(f"Removed marketplace: {target}", result=await plugin_handlers.marketplaceRemoveHandler(target, {}))
        elif action == "update":
            result = command_result("Updated marketplaces.", result=await plugin_handlers.marketplaceUpdateHandler(target, {}))
        else:
            marketplaces = await list_marketplaces()
            result = command_result(f"Marketplaces: {len(marketplaces['items'])}.", marketplaces=marketplaces["items"])
    else:
        result = command_result(PLUGIN_HELP, parsed=parsed)
    if onDone:
        onDone(result["value"])
    return result


__all__ = ["call", "local_call", "plugin_command"]
