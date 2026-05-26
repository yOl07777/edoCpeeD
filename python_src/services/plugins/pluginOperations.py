"""Local plugin operation helpers for the Python migration.

These functions mirror the TypeScript service boundary while staying local and
deterministic.  They update a small JSON registry under ``DEEPCODE_CONFIG_HOME``
and never clone marketplaces, run package managers, or execute plugin code.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

VALID_INSTALLABLE_SCOPES = ("user", "project", "local")
VALID_UPDATE_SCOPES = ("user", "project", "local", "managed")


def _cwd() -> Path:
    return Path(os.getenv("DEEPCODE_CWD") or os.getcwd()).resolve()


def _config_home() -> Path:
    root = os.getenv("DEEPCODE_CONFIG_HOME") or os.getenv("DEEPSEEK_CODE_HOME")
    return Path(root).expanduser().resolve() if root else (Path.home() / ".deepcode").resolve()


def _plugins_path() -> Path:
    return _config_home() / "plugins.json"


def _read_plugins() -> dict[str, Any]:
    try:
        data = json.loads(_plugins_path().read_text(encoding="utf-8"))
    except Exception:
        data = {}
    if not isinstance(data, dict):
        data = {}
    data.setdefault("plugins", {})
    data.setdefault("disabledAll", False)
    return data


def _write_plugins(data: dict[str, Any]) -> None:
    path = _plugins_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _plugin_id(plugin: str) -> str:
    return str(plugin).strip()


def _plugin_name(plugin_id: str) -> str:
    return plugin_id.split("@", 1)[0]


def _result(success: bool, message: str, plugin_id: str | None = None, **extra: Any) -> dict[str, Any]:
    result = {"success": success, "message": message}
    if plugin_id:
        result["pluginId"] = plugin_id
        result["pluginName"] = _plugin_name(plugin_id)
    result.update({k: v for k, v in extra.items() if v is not None})
    return result


async def isInstallableScope(*args: Any, **kwargs: Any) -> bool:
    scope = str(kwargs.get("scope") or (args[0] if args else ""))
    return scope in VALID_INSTALLABLE_SCOPES


async def assertInstallableScope(*args: Any, **kwargs: Any) -> str:
    scope = str(kwargs.get("scope") or (args[0] if args else ""))
    if scope not in VALID_INSTALLABLE_SCOPES:
        raise ValueError(f'Invalid scope "{scope}". Must be one of: {", ".join(VALID_INSTALLABLE_SCOPES)}')
    return scope


async def getProjectPathForScope(*args: Any, **kwargs: Any) -> str | None:
    scope = str(kwargs.get("scope") or (args[0] if args else ""))
    return str(_cwd()) if scope in {"project", "local"} else None


async def isPluginEnabledAtProjectScope(*args: Any, **kwargs: Any) -> bool:
    plugin_id = _plugin_id(str(kwargs.get("pluginId") or kwargs.get("plugin") or (args[0] if args else "")))
    entry = _read_plugins()["plugins"].get(plugin_id)
    return bool(isinstance(entry, dict) and entry.get("enabled") and entry.get("scope") in {"project", "local"})


async def getPluginInstallationFromV2(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    plugin_id = _plugin_id(str(kwargs.get("pluginId") or kwargs.get("plugin") or (args[0] if args else "")))
    entry = _read_plugins()["plugins"].get(plugin_id)
    if not isinstance(entry, dict):
        name = _plugin_name(plugin_id)
        for key, value in _read_plugins()["plugins"].items():
            if _plugin_name(key) == name and isinstance(value, dict):
                plugin_id, entry = key, value
                break
    if not isinstance(entry, dict):
        return None
    return {
        "pluginId": plugin_id,
        "pluginName": _plugin_name(plugin_id),
        "scope": entry.get("scope", "user"),
        "projectPath": entry.get("projectPath"),
        "version": entry.get("version", "local"),
        "enabled": bool(entry.get("enabled", True)),
        "source": entry.get("source", plugin_id),
    }


async def installPluginOp(*args: Any, **kwargs: Any) -> dict[str, Any]:
    plugin = _plugin_id(str(kwargs.get("plugin") or (args[0] if args else "")))
    scope = str(kwargs.get("scope") or (args[1] if len(args) > 1 else "user"))
    await assertInstallableScope(scope)
    if not plugin:
        return _result(False, "Plugin identifier is required")
    data = _read_plugins()
    project_path = await getProjectPathForScope(scope)
    data["plugins"][plugin] = {
        "source": kwargs.get("source") or plugin,
        "scope": scope,
        "version": kwargs.get("version") or "local",
        "enabled": True,
        "projectPath": project_path,
    }
    data["disabledAll"] = False
    _write_plugins(data)
    return _result(True, f'Installed plugin "{plugin}" at {scope} scope', plugin, scope=scope)


async def uninstallPluginOp(*args: Any, **kwargs: Any) -> dict[str, Any]:
    plugin = _plugin_id(str(kwargs.get("plugin") or (args[0] if args else "")))
    scope = kwargs.get("scope") or (args[1] if len(args) > 1 else None)
    data = _read_plugins()
    removed = data["plugins"].pop(plugin, None)
    if removed is None:
        return _result(False, f'Plugin "{plugin}" is not installed', plugin, scope=scope)
    _write_plugins(data)
    return _result(True, f'Uninstalled plugin "{plugin}"', plugin, scope=scope or removed.get("scope"))


async def setPluginEnabledOp(*args: Any, **kwargs: Any) -> dict[str, Any]:
    plugin = _plugin_id(str(kwargs.get("plugin") or kwargs.get("pluginId") or (args[0] if args else "")))
    enabled = bool(kwargs.get("enabled") if "enabled" in kwargs else (args[1] if len(args) > 1 else True))
    scope = kwargs.get("scope") or (args[2] if len(args) > 2 else None)
    data = _read_plugins()
    entry = data["plugins"].setdefault(
        plugin,
        {"source": plugin, "scope": scope or "user", "version": "local", "projectPath": await getProjectPathForScope(scope or "user")},
    )
    if scope:
        entry["scope"] = scope
        entry["projectPath"] = await getProjectPathForScope(scope)
    entry["enabled"] = enabled
    if enabled:
        data["disabledAll"] = False
    _write_plugins(data)
    verb = "Enabled" if enabled else "Disabled"
    return _result(True, f'{verb} plugin "{plugin}"', plugin, scope=entry.get("scope"))


async def enablePluginOp(*args: Any, **kwargs: Any) -> dict[str, Any]:
    plugin = kwargs.get("plugin") or (args[0] if args else "")
    scope = kwargs.get("scope") or (args[1] if len(args) > 1 else None)
    return await setPluginEnabledOp(plugin, True, scope)


async def disablePluginOp(*args: Any, **kwargs: Any) -> dict[str, Any]:
    plugin = kwargs.get("plugin") or (args[0] if args else "")
    scope = kwargs.get("scope") or (args[1] if len(args) > 1 else None)
    return await setPluginEnabledOp(plugin, False, scope)


async def disableAllPluginsOp(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _read_plugins()
    for entry in data["plugins"].values():
        if isinstance(entry, dict):
            entry["enabled"] = False
    data["disabledAll"] = True
    _write_plugins(data)
    return _result(True, f'Disabled {len(data["plugins"])} plugin(s)', count=len(data["plugins"]))


async def updatePluginOp(*args: Any, **kwargs: Any) -> dict[str, Any]:
    plugin = kwargs.get("plugin") if "plugin" in kwargs else (args[0] if args else None)
    scope = kwargs.get("scope") or (args[1] if len(args) > 1 else None)
    data = _read_plugins()
    names = [_plugin_id(str(plugin))] if plugin else list(data["plugins"])
    updated: list[str] = []
    for name in names:
        entry = data["plugins"].get(name)
        if not isinstance(entry, dict):
            continue
        old = str(entry.get("version", "local"))
        new = str(kwargs.get("version") or old)
        entry["oldVersion"] = old
        entry["version"] = new
        entry["updated"] = True
        updated.append(name)
    _write_plugins(data)
    if plugin and not updated:
        return _result(False, f'Plugin "{plugin}" is not installed', str(plugin), scope=scope)
    return {
        "success": True,
        "message": f'Updated {len(updated)} plugin(s)',
        "pluginId": updated[0] if len(updated) == 1 else None,
        "newVersion": kwargs.get("version"),
        "alreadyUpToDate": kwargs.get("version") is None,
        "scope": scope,
        "updated": updated,
    }


__all__ = [
    "VALID_INSTALLABLE_SCOPES",
    "VALID_UPDATE_SCOPES",
    "assertInstallableScope",
    "disableAllPluginsOp",
    "disablePluginOp",
    "enablePluginOp",
    "getPluginInstallationFromV2",
    "getProjectPathForScope",
    "installPluginOp",
    "isInstallableScope",
    "isPluginEnabledAtProjectScope",
    "setPluginEnabledOp",
    "uninstallPluginOp",
    "updatePluginOp",
]
