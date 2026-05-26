"""Local MCP configuration management for the Python migration."""

from __future__ import annotations

import json
import os
import re
from copy import deepcopy
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .types import McpJsonConfigSchema, McpServerConfigSchema

ConfigRecord = dict[str, dict[str, Any]]

CCR_PROXY_PATH_MARKERS = ["/v2/session_ingress/shttp/mcp/", "/v2/ccr-sessions/"]
_USER_CONFIG_CACHE: dict[str, Any] = {}
_PROJECT_CONFIG_CACHE: dict[str, Any] = {}


def _cwd() -> Path:
    return Path(os.getenv("DEEPCODE_CWD") or os.getcwd()).resolve()


def _config_home() -> Path:
    return Path(os.getenv("DEEPCODE_CONFIG_HOME") or Path.home() / ".deepcode").resolve()


def _managed_home() -> Path:
    return Path(os.getenv("DEEPCODE_MANAGED_CONFIG_HOME") or _config_home() / "managed").resolve()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except FileNotFoundError:
        raise
    except Exception as exc:
        raise ValueError(str(exc)) from exc


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _user_config_path() -> Path:
    return _config_home() / "config.json"


def _project_config_path() -> Path:
    return _cwd() / ".deepseek_project.json"


def _get_user_config() -> dict[str, Any]:
    global _USER_CONFIG_CACHE
    if not _USER_CONFIG_CACHE:
        try:
            _USER_CONFIG_CACHE = _read_json(_user_config_path())
        except Exception:
            _USER_CONFIG_CACHE = {}
    return deepcopy(_USER_CONFIG_CACHE)


def _save_user_config(config: dict[str, Any]) -> None:
    global _USER_CONFIG_CACHE
    _USER_CONFIG_CACHE = deepcopy(config)
    _write_json(_user_config_path(), config)


def _get_project_config() -> dict[str, Any]:
    global _PROJECT_CONFIG_CACHE
    if not _PROJECT_CONFIG_CACHE:
        try:
            _PROJECT_CONFIG_CACHE = _read_json(_project_config_path())
        except Exception:
            _PROJECT_CONFIG_CACHE = {}
    return deepcopy(_PROJECT_CONFIG_CACHE)


def _save_project_config(config: dict[str, Any]) -> None:
    global _PROJECT_CONFIG_CACHE
    _PROJECT_CONFIG_CACHE = deepcopy(config)
    _write_json(_project_config_path(), config)


def _validation_error(
    message: str,
    *,
    file: str | None = None,
    path: str = "",
    scope: str = "project",
    severity: str = "fatal",
    suggestion: str | None = None,
    server_name: str | None = None,
) -> dict[str, Any]:
    error: dict[str, Any] = {
        "path": path,
        "message": message,
        "mcpErrorMetadata": {"scope": scope, "severity": severity},
    }
    if file:
        error["file"] = file
    if suggestion:
        error["suggestion"] = suggestion
    if server_name:
        error["mcpErrorMetadata"]["serverName"] = server_name
    return error


def _add_scope(servers: dict[str, Any] | None, scope: str) -> ConfigRecord:
    return {name: {**dict(config), "scope": scope} for name, config in (servers or {}).items()}


def _server_command_array(config: dict[str, Any]) -> list[str] | None:
    if config.get("type", "stdio") != "stdio":
        return None
    command = config.get("command")
    if not command:
        return None
    return [str(command), *[str(arg) for arg in config.get("args", [])]]


def _server_url(config: dict[str, Any]) -> str | None:
    return str(config["url"]) if config.get("url") else None


def getEnterpriseMcpFilePath() -> str:
    return str(_managed_home() / "managed-mcp.json")


def unwrapCcrProxyUrl(url: str) -> str:
    if not any(marker in str(url) for marker in CCR_PROXY_PATH_MARKERS):
        return str(url)
    try:
        parsed = urlparse(str(url))
        original = parse_qs(parsed.query).get("mcp_url", [None])[0]
        return original or str(url)
    except Exception:
        return str(url)


def getMcpServerSignature(config: dict[str, Any]) -> str | None:
    command = _server_command_array(config)
    if command:
        return "stdio:" + json.dumps(command, ensure_ascii=False, separators=(",", ":"))
    url = _server_url(config)
    if url:
        return "url:" + unwrapCcrProxyUrl(url)
    return None


def dedupPluginMcpServers(
    pluginServers: ConfigRecord,
    manualServers: ConfigRecord,
) -> dict[str, Any]:
    manual_sigs = {
        sig: name
        for name, config in manualServers.items()
        if (sig := getMcpServerSignature(config))
    }
    servers: ConfigRecord = {}
    suppressed: list[dict[str, str]] = []
    seen_plugin_sigs: dict[str, str] = {}
    for name, config in pluginServers.items():
        sig = getMcpServerSignature(config)
        if sig is None:
            servers[name] = config
            continue
        duplicate = manual_sigs.get(sig) or seen_plugin_sigs.get(sig)
        if duplicate:
            suppressed.append({"name": name, "duplicateOf": duplicate})
            continue
        seen_plugin_sigs[sig] = name
        servers[name] = config
    return {"servers": servers, "suppressed": suppressed}


def dedupClaudeAiMcpServers(
    claudeAiServers: ConfigRecord,
    manualServers: ConfigRecord,
) -> dict[str, Any]:
    enabled_manual = {name: cfg for name, cfg in manualServers.items() if not isMcpServerDisabled(name)}
    return dedupPluginMcpServers(claudeAiServers, enabled_manual)


def _entry_matches_name(entry: Any, name: str) -> bool:
    return isinstance(entry, dict) and entry.get("serverName") == name


def _entry_matches_command(entry: Any, command: list[str] | None) -> bool:
    return bool(command) and isinstance(entry, dict) and entry.get("serverCommand") == command


def _url_pattern_matches(url: str, pattern: str) -> bool:
    regex = "^" + re.escape(pattern).replace("\\*", ".*") + "$"
    return re.match(regex, url) is not None


def _entry_matches_url(entry: Any, url: str | None) -> bool:
    return bool(url) and isinstance(entry, dict) and bool(entry.get("serverUrl")) and _url_pattern_matches(str(url), str(entry["serverUrl"]))


def _settings() -> dict[str, Any]:
    settings: dict[str, Any] = {}
    for key in ("DEEPCODE_MCP_SETTINGS", "DEEPSEEK_MCP_SETTINGS"):
        raw = os.getenv(key)
        if raw:
            try:
                settings.update(json.loads(raw))
            except Exception:
                pass
    return settings


def shouldAllowManagedMcpServersOnly() -> bool:
    return bool(_settings().get("allowManagedMcpServersOnly"))


def _is_denied(name: str, config: dict[str, Any] | None = None) -> bool:
    command = _server_command_array(config or {})
    url = _server_url(config or {})
    for entry in _settings().get("deniedMcpServers", []) or []:
        if _entry_matches_name(entry, name) or _entry_matches_command(entry, command) or _entry_matches_url(entry, url):
            return True
    return False


def _is_allowed(name: str, config: dict[str, Any] | None = None) -> bool:
    if _is_denied(name, config):
        return False
    allowed = _settings().get("allowedMcpServers")
    if allowed is None:
        return True
    if not allowed:
        return False
    command = _server_command_array(config or {})
    url = _server_url(config or {})
    has_command_entries = any(isinstance(e, dict) and "serverCommand" in e for e in allowed)
    has_url_entries = any(isinstance(e, dict) and "serverUrl" in e for e in allowed)
    if command and has_command_entries:
        return any(_entry_matches_command(e, command) for e in allowed)
    if url and has_url_entries:
        return any(_entry_matches_url(e, url) for e in allowed)
    return any(_entry_matches_name(e, name) for e in allowed)


def filterMcpServersByPolicy(configs: dict[str, Any]) -> dict[str, Any]:
    allowed: dict[str, Any] = {}
    blocked: list[str] = []
    for name, config in configs.items():
        if isinstance(config, dict) and config.get("type") == "sdk":
            allowed[name] = config
        elif _is_allowed(name, config if isinstance(config, dict) else None):
            allowed[name] = config
        else:
            blocked.append(name)
    return {"allowed": allowed, "blocked": blocked}


def _expand_string(value: str) -> tuple[str, list[str]]:
    missing: list[str] = []

    def replace(match: re.Match[str]) -> str:
        key = match.group(1) or match.group(2) or match.group(4) or ""
        default = match.group(3)
        if key in os.environ:
            return os.environ[key]
        if default is not None:
            return default
        missing.append(key)
        return ""

    expanded = re.sub(r"\$(\w+)|\$\{([^}:]+)(?::-(.*?))?\}|%([^%]+)%", replace, value)
    return expanded, missing


def _expand_env_vars(config: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    expanded = deepcopy(config)
    missing: list[str] = []
    keys = ["command", "url"]
    for key in keys:
        if isinstance(expanded.get(key), str):
            expanded[key], vars_ = _expand_string(expanded[key])
            missing.extend(vars_)
    if isinstance(expanded.get("args"), list):
        args = []
        for arg in expanded["args"]:
            text, vars_ = _expand_string(str(arg))
            args.append(text)
            missing.extend(vars_)
        expanded["args"] = args
    for map_key in ("env", "headers"):
        if isinstance(expanded.get(map_key), dict):
            mapped = {}
            for key, value in expanded[map_key].items():
                text, vars_ = _expand_string(str(value))
                mapped[str(key)] = text
                missing.extend(vars_)
            expanded[map_key] = mapped
    return expanded, sorted(set(missing))


def parseMcpConfig(params: dict[str, Any]) -> dict[str, Any]:
    config_object = params.get("configObject")
    expand_vars = bool(params.get("expandVars"))
    scope = str(params.get("scope") or "project")
    file_path = params.get("filePath")

    schema_result = McpJsonConfigSchema().safeParse(config_object)
    if not schema_result.success:
        return {
            "config": None,
            "errors": [
                _validation_error(
                    "Does not adhere to MCP server configuration schema",
                    file=file_path,
                    scope=scope,
                )
            ],
        }

    errors: list[dict[str, Any]] = []
    validated_servers: dict[str, Any] = {}
    for name, config in schema_result.data.get("mcpServers", {}).items():
        config_to_check = deepcopy(config)
        if expand_vars:
            config_to_check, missing = _expand_env_vars(config_to_check)
            if missing:
                errors.append(
                    _validation_error(
                        f"Missing environment variables: {', '.join(missing)}",
                        file=file_path,
                        path=f"mcpServers.{name}",
                        scope=scope,
                        severity="warning",
                        suggestion=f"Set the following environment variables: {', '.join(missing)}",
                        server_name=name,
                    )
                )
        if os.name == "nt" and config_to_check.get("type", "stdio") == "stdio":
            command = str(config_to_check.get("command", ""))
            if command == "npx" or command.endswith("\\npx") or command.endswith("/npx"):
                errors.append(
                    _validation_error(
                        "Windows requires 'cmd /c' wrapper to execute npx",
                        file=file_path,
                        path=f"mcpServers.{name}",
                        scope=scope,
                        severity="warning",
                        suggestion='Change command to "cmd" with args ["/c", "npx", ...].',
                        server_name=name,
                    )
                )
        validated_servers[name] = config_to_check
    return {"config": {"mcpServers": validated_servers}, "errors": errors}


def parseMcpConfigFromFilePath(params: dict[str, Any]) -> dict[str, Any]:
    file_path = Path(params["filePath"])
    scope = str(params.get("scope") or "project")
    try:
        parsed = _read_json(file_path)
    except FileNotFoundError:
        return {
            "config": None,
            "errors": [
                _validation_error(
                    f"MCP config file not found: {file_path}",
                    file=str(file_path),
                    scope=scope,
                    suggestion="Check that the file path is correct",
                )
            ],
        }
    except Exception:
        return {
            "config": None,
            "errors": [
                _validation_error(
                    "MCP config is not a valid JSON",
                    file=str(file_path),
                    scope=scope,
                    suggestion="Fix the JSON syntax errors in the file",
                )
            ],
        }
    return parseMcpConfig(
        {
            "configObject": parsed,
            "expandVars": bool(params.get("expandVars")),
            "scope": scope,
            "filePath": str(file_path),
        }
    )


def getProjectMcpConfigsFromCwd() -> dict[str, Any]:
    result = parseMcpConfigFromFilePath(
        {"filePath": str(_cwd() / ".mcp.json"), "expandVars": True, "scope": "project"}
    )
    if not result["config"]:
        non_missing = [e for e in result["errors"] if not e["message"].startswith("MCP config file not found")]
        return {"servers": {}, "errors": non_missing}
    return {
        "servers": _add_scope(result["config"].get("mcpServers"), "project"),
        "errors": result.get("errors", []),
    }


def getMcpConfigsByScope(scope: str) -> dict[str, Any]:
    if scope == "project":
        return getProjectMcpConfigsFromCwd()
    if scope == "user":
        servers = _get_user_config().get("mcpServers", {})
        result = parseMcpConfig({"configObject": {"mcpServers": servers}, "expandVars": True, "scope": "user"})
        return {"servers": _add_scope((result["config"] or {}).get("mcpServers"), "user"), "errors": result["errors"]}
    if scope == "local":
        servers = _get_project_config().get("mcpServers", {})
        result = parseMcpConfig({"configObject": {"mcpServers": servers}, "expandVars": True, "scope": "local"})
        return {"servers": _add_scope((result["config"] or {}).get("mcpServers"), "local"), "errors": result["errors"]}
    if scope == "enterprise":
        result = parseMcpConfigFromFilePath(
            {"filePath": getEnterpriseMcpFilePath(), "expandVars": True, "scope": "enterprise"}
        )
        if not result["config"]:
            non_missing = [e for e in result["errors"] if not e["message"].startswith("MCP config file not found")]
            return {"servers": {}, "errors": non_missing}
        return {"servers": _add_scope(result["config"].get("mcpServers"), "enterprise"), "errors": result["errors"]}
    return {"servers": {}, "errors": []}


def getMcpConfigByName(name: str) -> dict[str, Any] | None:
    for scope in ("enterprise", "local", "project", "user"):
        servers = getMcpConfigsByScope(scope)["servers"]
        if name in servers:
            return servers[name]
    return None


def doesEnterpriseMcpConfigExist() -> bool:
    return parseMcpConfigFromFilePath(
        {"filePath": getEnterpriseMcpFilePath(), "expandVars": True, "scope": "enterprise"}
    )["config"] is not None


async def getClaudeCodeMcpConfigs(
    dynamicServers: ConfigRecord | None = None,
    extraDedupTargets: Any | None = None,
) -> dict[str, Any]:
    enterprise = getMcpConfigsByScope("enterprise")["servers"]
    if doesEnterpriseMcpConfigExist():
        return {"servers": filterMcpServersByPolicy(enterprise)["allowed"], "errors": []}
    merged: ConfigRecord = {}
    for scope in ("user", "project", "local"):
        merged.update(getMcpConfigsByScope(scope)["servers"])
    merged.update(dynamicServers or {})
    filtered = filterMcpServersByPolicy(merged)["allowed"]
    return {"servers": filtered, "errors": []}


async def getAllMcpConfigs() -> dict[str, Any]:
    return await getClaudeCodeMcpConfigs()


async def addMcpConfig(name: str, config: Any, scope: str) -> None:
    if re.search(r"[^a-zA-Z0-9_-]", name):
        raise ValueError(f"Invalid name {name}. Names can only contain letters, numbers, hyphens, and underscores.")
    if doesEnterpriseMcpConfigExist():
        raise ValueError("Cannot add MCP server: enterprise MCP configuration is active")
    parsed = McpServerConfigSchema().safeParse(config)
    if not parsed.success:
        raise ValueError("Invalid configuration: " + (parsed.error.issues[0].message if parsed.error else "unknown"))
    validated = parsed.data
    if _is_denied(name, validated) or not _is_allowed(name, validated):
        raise ValueError(f'Cannot add MCP server "{name}": not allowed by enterprise policy')

    if scope == "project":
        current = getProjectMcpConfigsFromCwd()["servers"]
        if name in current:
            raise ValueError(f"MCP server {name} already exists in .mcp.json")
        servers = {k: {kk: vv for kk, vv in v.items() if kk != "scope"} for k, v in current.items()}
        servers[name] = validated
        _write_json(_cwd() / ".mcp.json", {"mcpServers": servers})
        return
    if scope == "user":
        cfg = _get_user_config()
        servers = dict(cfg.get("mcpServers", {}))
        if name in servers:
            raise ValueError(f"MCP server {name} already exists in user config")
        servers[name] = validated
        cfg["mcpServers"] = servers
        _save_user_config(cfg)
        return
    if scope == "local":
        cfg = _get_project_config()
        servers = dict(cfg.get("mcpServers", {}))
        if name in servers:
            raise ValueError(f"MCP server {name} already exists in local config")
        servers[name] = validated
        cfg["mcpServers"] = servers
        _save_project_config(cfg)
        return
    raise ValueError(f"Cannot add MCP server to scope: {scope}")


async def removeMcpConfig(name: str, scope: str) -> None:
    if scope == "project":
        current = getProjectMcpConfigsFromCwd()["servers"]
        if name not in current:
            raise ValueError(f"No MCP server found with name: {name} in .mcp.json")
        servers = {k: {kk: vv for kk, vv in v.items() if kk != "scope"} for k, v in current.items() if k != name}
        _write_json(_cwd() / ".mcp.json", {"mcpServers": servers})
        return
    if scope == "user":
        cfg = _get_user_config()
        servers = dict(cfg.get("mcpServers", {}))
        if name not in servers:
            raise ValueError(f"No user-scoped MCP server found with name: {name}")
        servers.pop(name, None)
        cfg["mcpServers"] = servers
        _save_user_config(cfg)
        return
    if scope == "local":
        cfg = _get_project_config()
        servers = dict(cfg.get("mcpServers", {}))
        if name not in servers:
            raise ValueError(f"No project-local MCP server found with name: {name}")
        servers.pop(name, None)
        cfg["mcpServers"] = servers
        _save_project_config(cfg)
        return
    raise ValueError(f"Cannot remove MCP server from scope: {scope}")


def areMcpConfigsAllowedWithEnterpriseMcpConfig(configs: ConfigRecord) -> bool:
    return all(config.get("type") == "sdk" and config.get("name") == "claude-vscode" for config in configs.values())


def isMcpServerDisabled(name: str) -> bool:
    return name in (_get_project_config().get("disabledMcpServers") or [])


def _toggle_membership(items: list[str], name: str, should_contain: bool) -> list[str]:
    contains = name in items
    if contains == should_contain:
        return items
    return [*items, name] if should_contain else [item for item in items if item != name]


def setMcpServerEnabled(name: str, enabled: bool) -> None:
    cfg = _get_project_config()
    disabled = list(cfg.get("disabledMcpServers") or [])
    cfg["disabledMcpServers"] = _toggle_membership(disabled, name, not enabled)
    _save_project_config(cfg)


__all__ = [
    "addMcpConfig",
    "areMcpConfigsAllowedWithEnterpriseMcpConfig",
    "dedupClaudeAiMcpServers",
    "dedupPluginMcpServers",
    "doesEnterpriseMcpConfigExist",
    "filterMcpServersByPolicy",
    "getAllMcpConfigs",
    "getClaudeCodeMcpConfigs",
    "getEnterpriseMcpFilePath",
    "getMcpConfigByName",
    "getMcpConfigsByScope",
    "getMcpServerSignature",
    "getProjectMcpConfigsFromCwd",
    "isMcpServerDisabled",
    "parseMcpConfig",
    "parseMcpConfigFromFilePath",
    "removeMcpConfig",
    "setMcpServerEnabled",
    "shouldAllowManagedMcpServersOnly",
    "unwrapCcrProxyUrl",
]
