"""Local MCP CLI handlers."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _config_home() -> Path:
    root = os.getenv("DEEPCODE_CONFIG_HOME") or os.getenv("DEEPSEEK_CODE_HOME")
    return Path(root).expanduser() if root else Path.home() / ".deepcode"


def _mcp_path() -> Path:
    return _config_home() / "mcp_servers.json"


def _choices_path() -> Path:
    return _config_home() / "mcp_choices.json"


def _read_config() -> dict[str, Any]:
    try:
        data = json.loads(_mcp_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"servers": {}}
    if not isinstance(data, dict):
        return {"servers": {}}
    data.setdefault("servers", {})
    return data


def _write_config(data: dict[str, Any]) -> None:
    path = _mcp_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _server_status(server: dict[str, Any]) -> str:
    if server.get("disabled"):
        return "disabled"
    if server.get("command") or server.get("url"):
        return "configured"
    return "invalid"


async def mcpAddJsonHandler(name: str, json_config: str | dict[str, Any], options: dict[str, Any] | None = None) -> dict[str, Any]:
    if isinstance(json_config, str):
        parsed = json.loads(json_config)
    else:
        parsed = dict(json_config)
    if not isinstance(parsed, dict):
        raise ValueError("MCP server config must be an object")
    config = _read_config()
    config["servers"][name] = parsed
    if options:
        config["servers"][name]["scope"] = options.get("scope", config["servers"][name].get("scope", "user"))
    _write_config(config)
    return {"added": True, "name": name, "server": config["servers"][name]}


async def mcpAddFromDesktopHandler(options: dict[str, Any] | None = None) -> dict[str, Any]:
    options = options or {}
    source = Path(options.get("path") or (Path.home() / ".claude_desktop_config.json"))
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"added": 0, "source": str(source), "servers": []}
    servers = data.get("mcpServers") or data.get("servers") if isinstance(data, dict) else {}
    if not isinstance(servers, dict):
        return {"added": 0, "source": str(source), "servers": []}
    config = _read_config()
    for name, server in servers.items():
        if isinstance(server, dict):
            config["servers"][str(name)] = dict(server)
    _write_config(config)
    return {"added": len(servers), "source": str(source), "servers": sorted(servers)}


async def mcpListHandler() -> dict[str, Any]:
    config = _read_config()
    servers = [
        {"name": name, "status": _server_status(server), **server}
        for name, server in sorted(config.get("servers", {}).items())
        if isinstance(server, dict)
    ]
    return {"servers": servers, "path": str(_mcp_path())}


async def mcpGetHandler(name: str) -> dict[str, Any] | None:
    server = _read_config().get("servers", {}).get(name)
    if not isinstance(server, dict):
        return None
    return {"name": name, "status": _server_status(server), "server": server}


async def mcpRemoveHandler(name: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
    config = _read_config()
    removed = config.get("servers", {}).pop(name, None) is not None
    _write_config(config)
    return {"removed": removed, "name": name}


async def mcpResetChoicesHandler() -> dict[str, Any]:
    path = _choices_path()
    existed = path.exists()
    try:
        path.unlink()
    except FileNotFoundError:
        pass
    return {"reset": True, "removed": existed, "path": str(path)}


async def mcpServeHandler(options: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    merged = {**(options or {}), **kwargs}
    return {"serving": True, "transport": merged.get("transport", "stdio"), "cwd": str(Path.cwd())}
