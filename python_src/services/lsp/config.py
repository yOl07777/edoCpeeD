"""LSP server configuration for the local Python migration."""

from __future__ import annotations

from typing import Any

_DEFAULT_SERVERS = [
    {"id": "python", "extensions": [".py"], "command": "python-lsp-server", "enabled": True},
    {"id": "typescript", "extensions": [".ts", ".tsx", ".js", ".jsx"], "command": "typescript-language-server", "enabled": True},
]


async def getAllLspServers(config: dict[str, Any] | list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    if config is None:
        return [dict(server) for server in _DEFAULT_SERVERS]
    if isinstance(config, list):
        return [dict(server) for server in config]
    servers = config.get("servers") if isinstance(config, dict) else None
    if isinstance(servers, list):
        return [dict(server) for server in servers]
    return [dict(server) for server in _DEFAULT_SERVERS]
