"""Local plugin and marketplace CLI handlers."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


VALID_INSTALLABLE_SCOPES = {"user", "project", "local"}
VALID_UPDATE_SCOPES = {"user", "project", "local"}


def _config_home() -> Path:
    root = os.getenv("DEEPCODE_CONFIG_HOME") or os.getenv("DEEPSEEK_CODE_HOME")
    return Path(root).expanduser() if root else Path.home() / ".deepcode"


def _plugins_path() -> Path:
    return _config_home() / "plugins.json"


def _marketplaces_path() -> Path:
    return _config_home() / "marketplaces.json"


def _read(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default
    return data if isinstance(data, dict) else default


def _write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _plugins() -> dict[str, Any]:
    data = _read(_plugins_path(), {"plugins": {}})
    data.setdefault("plugins", {})
    return data


def _marketplaces() -> dict[str, Any]:
    data = _read(_marketplaces_path(), {"marketplaces": {}})
    data.setdefault("marketplaces", {})
    return data


def handleMarketplaceError(error: Exception | str, action: str) -> dict[str, str]:
    return {"action": action, "error": str(error)}


async def marketplaceAddHandler(source: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
    options = options or {}
    name = options.get("name") or Path(source).stem or source.replace("/", "-")
    data = _marketplaces()
    data["marketplaces"][name] = {"source": source, "scope": options.get("scope", "user")}
    _write(_marketplaces_path(), data)
    return {"added": True, "name": name, "source": source}


async def marketplaceListHandler(options: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"marketplaces": _marketplaces()["marketplaces"], "path": str(_marketplaces_path())}


async def marketplaceRemoveHandler(name: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
    data = _marketplaces()
    removed = data["marketplaces"].pop(name, None) is not None
    _write(_marketplaces_path(), data)
    return {"removed": removed, "name": name}


async def marketplaceUpdateHandler(name: str | None = None, options: dict[str, Any] | None = None) -> dict[str, Any]:
    data = _marketplaces()
    names = [name] if name else list(data["marketplaces"])
    for item in names:
        if item in data["marketplaces"]:
            data["marketplaces"][item]["updated"] = True
    _write(_marketplaces_path(), data)
    return {"updated": names}


async def pluginInstallHandler(plugin: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
    options = options or {}
    scope = options.get("scope", "user")
    if scope not in VALID_INSTALLABLE_SCOPES:
        raise ValueError(f"Invalid plugin scope: {scope}")
    data = _plugins()
    data["plugins"][plugin] = {
        "source": options.get("source", plugin),
        "scope": scope,
        "version": options.get("version", "local"),
        "enabled": True,
    }
    _write(_plugins_path(), data)
    return {"installed": True, "plugin": plugin, "scope": scope}


async def pluginUninstallHandler(plugin: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
    data = _plugins()
    removed = data["plugins"].pop(plugin, None) is not None
    _write(_plugins_path(), data)
    return {"removed": removed, "plugin": plugin}


async def pluginEnableHandler(plugin: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
    data = _plugins()
    data["plugins"].setdefault(plugin, {"source": plugin, "scope": "user", "version": "local"})
    data["plugins"][plugin]["enabled"] = True
    _write(_plugins_path(), data)
    return {"enabled": True, "plugin": plugin}


async def pluginDisableHandler(plugin: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
    data = _plugins()
    data["plugins"].setdefault(plugin, {"source": plugin, "scope": "user", "version": "local"})
    data["plugins"][plugin]["enabled"] = False
    _write(_plugins_path(), data)
    return {"enabled": False, "plugin": plugin}


async def pluginUpdateHandler(plugin: str | None = None, options: dict[str, Any] | None = None) -> dict[str, Any]:
    data = _plugins()
    names = [plugin] if plugin else list(data["plugins"])
    for name in names:
        if name in data["plugins"]:
            data["plugins"][name]["updated"] = True
    _write(_plugins_path(), data)
    return {"updated": names}


async def pluginListHandler(options: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"plugins": _plugins()["plugins"], "path": str(_plugins_path())}


async def pluginValidateHandler(manifestPath: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
    path = Path(manifestPath)
    errors: list[str] = []
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"success": False, "errors": [str(exc)], "path": str(path)}
    if not isinstance(manifest, dict):
        errors.append("Manifest must be an object")
    else:
        if not manifest.get("name"):
            errors.append("Missing name")
        if not manifest.get("version"):
            errors.append("Missing version")
    return {"success": not errors, "errors": errors, "path": str(path)}
