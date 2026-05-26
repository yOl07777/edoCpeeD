"""Utility functions for migrated MCP metadata and filtering."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from .mcpStringUtils import mcpInfoFromString


def _get(item: Any, *keys: str) -> Any:
    if isinstance(item, dict):
        for key in keys:
            if key in item:
                return item[key]
    else:
        for key in keys:
            if hasattr(item, key):
                return getattr(item, key)
    return None


def _server_name(server: Any) -> str:
    return str(_get(server, "serverName", "server", "name", "id") or "")


async def commandBelongsToServer(command: Any, server_name: str) -> bool:
    return _server_name(command).lower() == str(server_name or "").lower()


async def describeMcpConfigFilePath(path: str | Path) -> str:
    value = Path(path)
    try:
        return str(value.expanduser().resolve())
    except OSError:
        return str(value)


async def ensureConfigScope(config: dict[str, Any], default_scope: str = "local") -> dict[str, Any]:
    result = dict(config)
    result["scope"] = result.get("scope") or default_scope
    return result


async def ensureTransport(config: dict[str, Any], default_transport: str = "stdio") -> dict[str, Any]:
    result = dict(config)
    result["transport"] = result.get("transport") or default_transport
    return result


async def excludeCommandsByServer(commands: Iterable[Any], server_name: str) -> list[Any]:
    return [item for item in commands if not await commandBelongsToServer(item, server_name)]


async def excludeResourcesByServer(resources: Iterable[Any], server_name: str) -> list[Any]:
    return [item for item in resources if _server_name(item).lower() != str(server_name or "").lower()]


async def excludeStalePluginClients(clients: Iterable[Any]) -> list[Any]:
    return [client for client in clients if not _get(client, "stale", "isStale", "disposed")]


async def excludeToolsByServer(tools: Iterable[Any], server_name: str) -> list[Any]:
    return [item for item in tools if not await isToolFromMcpServer(item, server_name)]


async def extractAgentMcpServers(agent: Any) -> list[Any]:
    value = _get(agent, "mcpServers", "servers") or []
    if isinstance(value, dict):
        return [{"name": name, **(server if isinstance(server, dict) else {"config": server})} for name, server in value.items()]
    return list(value)


async def filterCommandsByServer(commands: Iterable[Any], server_name: str) -> list[Any]:
    return [item for item in commands if await commandBelongsToServer(item, server_name)]


async def filterMcpPromptsByServer(prompts: Iterable[Any], server_name: str) -> list[Any]:
    return [item for item in prompts if _server_name(item).lower() == str(server_name or "").lower()]


async def filterResourcesByServer(resources: Iterable[Any], server_name: str) -> list[Any]:
    return [item for item in resources if _server_name(item).lower() == str(server_name or "").lower()]


async def filterToolsByServer(tools: Iterable[Any], server_name: str) -> list[Any]:
    return [item for item in tools if await isToolFromMcpServer(item, server_name)]


async def getLoggingSafeMcpBaseUrl(url: str) -> str:
    parsed = urlsplit(str(url or ""))
    if not parsed.scheme:
        return str(url or "")
    netloc = parsed.hostname or ""
    if parsed.port:
        netloc = f"{netloc}:{parsed.port}"
    return urlunsplit((parsed.scheme, netloc, parsed.path.rstrip("/"), "", ""))


async def getMcpServerScopeFromToolName(tool_name: str) -> str | None:
    info = await mcpInfoFromString(tool_name)
    return info.get("serverName") if info.get("isMcp") else None


async def getProjectMcpServerStatus(server: dict[str, Any]) -> str:
    if server.get("disabled"):
        return "disabled"
    if server.get("error"):
        return "error"
    if server.get("connected"):
        return "connected"
    return "configured"


async def getScopeLabel(scope: str | None) -> str:
    labels = {"local": "Local", "project": "Project", "user": "User", "enterprise": "Enterprise"}
    return labels.get(str(scope or "").lower(), str(scope or "Unknown"))


async def hashMcpConfig(config: Any) -> str:
    payload = json.dumps(config, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


async def isMcpCommand(command: Any) -> bool:
    return bool(_get(command, "serverName", "server") or str(_get(command, "name") or "").startswith("mcp__"))


async def isMcpTool(tool: Any) -> bool:
    name = str(_get(tool, "name") or tool or "")
    return bool(_get(tool, "serverName", "server") or name.startswith("mcp__"))


async def isToolFromMcpServer(tool: Any, server_name: str) -> bool:
    name = str(_get(tool, "name") or tool or "")
    if name.startswith("mcp__"):
        info = await mcpInfoFromString(name)
        return str(info.get("serverName") or "").lower() == str(server_name or "").lower()
    server = _server_name(tool)
    if server and server != name:
        return server.lower() == str(server_name or "").lower()
    info = await mcpInfoFromString(name)
    return str(info.get("serverName") or "").lower() == str(server_name or "").lower()


async def parseHeaders(value: Any) -> dict[str, str]:
    """Parse headers from JSON, newline text, or ``Key: Value`` comma strings."""

    if value is None:
        return {}
    if isinstance(value, dict):
        return {str(k): str(v) for k, v in value.items() if v is not None}
    text = str(value).strip()
    if not text:
        return {}
    if text.startswith("{"):
        parsed = json.loads(text)
        if not isinstance(parsed, dict):
            raise ValueError("MCP headers JSON must be an object")
        return {str(k): str(v) for k, v in parsed.items() if v is not None}
    headers: dict[str, str] = {}
    for line in text.replace(",", "\n").splitlines():
        if not line.strip():
            continue
        key, sep, val = line.partition(":")
        if not sep:
            raise ValueError(f"Invalid header entry: {line}")
        headers[key.strip()] = val.strip()
    return headers
