"""Small MCP connection context used by the Python migration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable


_current_context: "MCPConnectionContext | None" = None


async def _default_reconnect(serverName: str) -> dict[str, Any]:
    return {
        "client": {"name": serverName, "type": "pending"},
        "tools": [],
        "commands": [],
        "resources": [],
    }


async def _default_toggle(serverName: str) -> None:
    return None


@dataclass
class MCPConnectionContext:
    reconnectMcpServer: Callable[[str], Awaitable[dict[str, Any]]] = _default_reconnect
    toggleMcpServer: Callable[[str], Awaitable[None]] = _default_toggle
    dynamicMcpConfig: dict[str, Any] | None = None
    isStrictMcpConfig: bool = False
    children: Any = None
    state: dict[str, Any] = field(default_factory=dict)


def useMcpReconnect() -> Callable[[str], Awaitable[dict[str, Any]]]:
    if _current_context is None:
        raise RuntimeError("useMcpReconnect must be used within MCPConnectionManager")
    return _current_context.reconnectMcpServer


def useMcpToggleEnabled() -> Callable[[str], Awaitable[None]]:
    if _current_context is None:
        raise RuntimeError("useMcpToggleEnabled must be used within MCPConnectionManager")
    return _current_context.toggleMcpServer


def MCPConnectionManager(props: dict[str, Any] | None = None, **kwargs: Any) -> Any:
    global _current_context
    merged = dict(props or {})
    merged.update(kwargs)
    reconnect = merged.get("reconnectMcpServer") or _default_reconnect
    toggle = merged.get("toggleMcpServer") or _default_toggle
    _current_context = MCPConnectionContext(
        reconnectMcpServer=reconnect,
        toggleMcpServer=toggle,
        dynamicMcpConfig=merged.get("dynamicMcpConfig"),
        isStrictMcpConfig=bool(merged.get("isStrictMcpConfig", False)),
        children=merged.get("children"),
        state=merged.get("state") or {},
    )
    return merged.get("children")


def clearMcpConnectionContext() -> None:
    global _current_context
    _current_context = None


__all__ = [
    "MCPConnectionContext",
    "MCPConnectionManager",
    "clearMcpConnectionContext",
    "useMcpReconnect",
    "useMcpToggleEnabled",
]
