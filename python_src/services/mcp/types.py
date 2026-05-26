"""MCP configuration schemas and aliases for the Python migration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

ConfigScope = str
Transport = str
McpServerConfig = dict[str, Any]
ScopedMcpServerConfig = dict[str, Any]
McpJsonConfig = dict[str, dict[str, McpServerConfig]]

CONFIG_SCOPES = {"local", "user", "project", "dynamic", "enterprise", "claudeai", "managed"}
TRANSPORTS = {"stdio", "sse", "sse-ide", "http", "ws", "sdk", "claudeai-proxy"}


@dataclass
class SchemaIssue:
    path: list[str]
    message: str


@dataclass
class SchemaError:
    issues: list[SchemaIssue]


@dataclass
class SchemaResult:
    success: bool
    data: Any = None
    error: SchemaError | None = None


class _Schema:
    def __init__(self, validator):
        self._validator = validator

    def safeParse(self, value: Any) -> SchemaResult:
        try:
            return SchemaResult(True, self._validator(value), None)
        except ValueError as exc:
            return SchemaResult(False, None, SchemaError([SchemaIssue([], str(exc))]))

    def parse(self, value: Any) -> Any:
        return self._validator(value)


def _validate_server(config: Any) -> McpServerConfig:
    if not isinstance(config, dict):
        raise ValueError("MCP server config must be an object")
    server = dict(config)
    transport = server.get("type", "stdio")
    if transport not in TRANSPORTS:
        raise ValueError(f"Unsupported MCP transport: {transport}")
    if transport in {"stdio", None}:
        if not server.get("command"):
            raise ValueError("Command cannot be empty")
        server.setdefault("args", [])
        if not isinstance(server["args"], list):
            raise ValueError("args must be an array")
    elif transport in {"sse", "http", "ws", "sse-ide", "ws-ide", "claudeai-proxy"}:
        if not server.get("url"):
            raise ValueError("url cannot be empty")
    elif transport == "sdk" and not server.get("name"):
        raise ValueError("sdk server name cannot be empty")
    return server


def _validate_mcp_json(config: Any) -> McpJsonConfig:
    if not isinstance(config, dict):
        raise ValueError("MCP config must be an object")
    servers = config.get("mcpServers", {})
    if not isinstance(servers, dict):
        raise ValueError("mcpServers must be an object")
    return {"mcpServers": {str(name): _validate_server(value) for name, value in servers.items()}}


def ConfigScopeSchema() -> _Schema:
    return _Schema(lambda value: value if value in CONFIG_SCOPES else (_ for _ in ()).throw(ValueError("Invalid config scope")))


def TransportSchema() -> _Schema:
    return _Schema(lambda value: value if value in TRANSPORTS else (_ for _ in ()).throw(ValueError("Invalid transport")))


def McpServerConfigSchema() -> _Schema:
    return _Schema(_validate_server)


def McpJsonConfigSchema() -> _Schema:
    return _Schema(_validate_mcp_json)


McpStdioServerConfigSchema = McpServerConfigSchema
McpSSEServerConfigSchema = McpServerConfigSchema
McpSSEIDEServerConfigSchema = McpServerConfigSchema
McpHTTPServerConfigSchema = McpServerConfigSchema
McpWebSocketIDEServerConfigSchema = McpServerConfigSchema
McpWebSocketServerConfigSchema = McpServerConfigSchema
McpSdkServerConfigSchema = McpServerConfigSchema
McpClaudeAIProxyServerConfigSchema = McpServerConfigSchema


__all__ = [
    "CONFIG_SCOPES",
    "TRANSPORTS",
    "ConfigScope",
    "ConfigScopeSchema",
    "McpClaudeAIProxyServerConfigSchema",
    "McpHTTPServerConfigSchema",
    "McpJsonConfig",
    "McpJsonConfigSchema",
    "McpSSEIDEServerConfigSchema",
    "McpSSEServerConfigSchema",
    "McpSdkServerConfigSchema",
    "McpServerConfig",
    "McpServerConfigSchema",
    "McpStdioServerConfigSchema",
    "McpWebSocketIDEServerConfigSchema",
    "McpWebSocketServerConfigSchema",
    "SchemaError",
    "SchemaIssue",
    "SchemaResult",
    "ScopedMcpServerConfig",
    "Transport",
    "TransportSchema",
]
