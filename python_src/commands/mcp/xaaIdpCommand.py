"""MCP XAA IdP command shim.

XAA is a Claude-specific enterprise MCP auth extension. The DeepSeek Python
migration exposes structured local metadata instead of performing browser
login or keychain writes.
"""

from __future__ import annotations

from typing import Any

_XAA_STATE: dict[str, Any] = {"configured": False, "issuer": None, "clientId": None, "callbackPort": None}


async def setupXaaIdp(issuer: str, clientId: str, callbackPort: int | None = None) -> dict[str, Any]:
    if not issuer.startswith(("https://", "http://localhost", "http://127.0.0.1")):
        raise ValueError("XAA issuer must use https:// or loopback http://")
    _XAA_STATE.update({"configured": True, "issuer": issuer, "clientId": clientId, "callbackPort": callbackPort})
    return await showXaaIdp()


async def showXaaIdp() -> dict[str, Any]:
    return dict(_XAA_STATE)


async def clearXaaIdp() -> dict[str, Any]:
    _XAA_STATE.update({"configured": False, "issuer": None, "clientId": None, "callbackPort": None})
    return await showXaaIdp()


def registerMcpXaaIdpCommand(mcp: Any) -> dict[str, Any]:
    descriptor = {
        "name": "xaa",
        "description": "Manage local XAA IdP metadata for MCP compatibility",
        "handlers": {"setup": setupXaaIdp, "show": showXaaIdp, "clear": clearXaaIdp},
    }
    if isinstance(mcp, list):
        mcp.append(descriptor)
    elif isinstance(mcp, dict):
        mcp.setdefault("subcommands", []).append(descriptor)
    return descriptor
