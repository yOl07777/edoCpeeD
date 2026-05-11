"""
Python migration draft for `src/services/mcp/auth.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

class AuthenticationCancelledError:
    """Migrated placeholder for TypeScript class `AuthenticationCancelledError`."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs

class ClaudeAuthProvider:
    """Migrated placeholder for TypeScript class `ClaudeAuthProvider`."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs

async def clearMcpClientConfig(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `clearMcpClientConfig`."""
    raise NotImplementedError(
        "services.mcp.auth.clearMcpClientConfig still needs business-logic migration"
    )

async def clearServerTokensFromLocalStorage(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `clearServerTokensFromLocalStorage`."""
    raise NotImplementedError(
        "services.mcp.auth.clearServerTokensFromLocalStorage still needs business-logic migration"
    )

async def getMcpClientConfig(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getMcpClientConfig`."""
    raise NotImplementedError(
        "services.mcp.auth.getMcpClientConfig still needs business-logic migration"
    )

async def getServerKey(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getServerKey`."""
    raise NotImplementedError(
        "services.mcp.auth.getServerKey still needs business-logic migration"
    )

async def hasMcpDiscoveryButNoToken(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `hasMcpDiscoveryButNoToken`."""
    raise NotImplementedError(
        "services.mcp.auth.hasMcpDiscoveryButNoToken still needs business-logic migration"
    )

async def normalizeOAuthErrorBody(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `normalizeOAuthErrorBody`."""
    raise NotImplementedError(
        "services.mcp.auth.normalizeOAuthErrorBody still needs business-logic migration"
    )

async def performMCPOAuthFlow(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `performMCPOAuthFlow`."""
    raise NotImplementedError(
        "services.mcp.auth.performMCPOAuthFlow still needs business-logic migration"
    )

async def readClientSecret(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `readClientSecret`."""
    raise NotImplementedError(
        "services.mcp.auth.readClientSecret still needs business-logic migration"
    )

async def revokeServerTokens(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `revokeServerTokens`."""
    raise NotImplementedError(
        "services.mcp.auth.revokeServerTokens still needs business-logic migration"
    )

async def saveMcpClientSecret(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `saveMcpClientSecret`."""
    raise NotImplementedError(
        "services.mcp.auth.saveMcpClientSecret still needs business-logic migration"
    )

async def wrapFetchWithStepUpDetection(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `wrapFetchWithStepUpDetection`."""
    raise NotImplementedError(
        "services.mcp.auth.wrapFetchWithStepUpDetection still needs business-logic migration"
    )
