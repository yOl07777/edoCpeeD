"""CLI-style wrappers around local plugin operations."""

from __future__ import annotations

from typing import Any

from .pluginOperations import (
    VALID_INSTALLABLE_SCOPES,
    VALID_UPDATE_SCOPES,
    disableAllPluginsOp,
    disablePluginOp,
    enablePluginOp,
    installPluginOp,
    uninstallPluginOp,
    updatePluginOp,
)


def _ok(command: str, result: dict[str, Any]) -> dict[str, Any]:
    return {"command": command, "ok": bool(result.get("success", True)), "result": result, "message": result.get("message", "")}


async def installPlugin(*args: Any, **kwargs: Any) -> dict[str, Any]:
    plugin = kwargs.get("plugin") or (args[0] if args else "")
    scope = kwargs.get("scope") or (args[1] if len(args) > 1 else "user")
    return _ok("install", await installPluginOp(plugin, scope))


async def uninstallPlugin(*args: Any, **kwargs: Any) -> dict[str, Any]:
    plugin = kwargs.get("plugin") or (args[0] if args else "")
    scope = kwargs.get("scope") or (args[1] if len(args) > 1 else "user")
    keepData = bool(kwargs.get("keepData") if "keepData" in kwargs else (args[2] if len(args) > 2 else False))
    result = await uninstallPluginOp(plugin, scope, keepData=keepData)
    result["keepData"] = keepData
    return _ok("uninstall", result)


async def enablePlugin(*args: Any, **kwargs: Any) -> dict[str, Any]:
    plugin = kwargs.get("plugin") or (args[0] if args else "")
    scope = kwargs.get("scope") or (args[1] if len(args) > 1 else None)
    return _ok("enable", await enablePluginOp(plugin, scope))


async def disablePlugin(*args: Any, **kwargs: Any) -> dict[str, Any]:
    plugin = kwargs.get("plugin") or (args[0] if args else "")
    scope = kwargs.get("scope") or (args[1] if len(args) > 1 else None)
    return _ok("disable", await disablePluginOp(plugin, scope))


async def disableAllPlugins(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return _ok("disable-all", await disableAllPluginsOp())


async def updatePluginCli(*args: Any, **kwargs: Any) -> dict[str, Any]:
    plugin = kwargs.get("plugin") if "plugin" in kwargs else (args[0] if args else None)
    scope = kwargs.get("scope") or (args[1] if len(args) > 1 else None)
    return _ok("update", await updatePluginOp(plugin, scope))


__all__ = [
    "VALID_INSTALLABLE_SCOPES",
    "VALID_UPDATE_SCOPES",
    "disableAllPlugins",
    "disablePlugin",
    "enablePlugin",
    "installPlugin",
    "uninstallPlugin",
    "updatePluginCli",
]
