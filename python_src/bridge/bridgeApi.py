"""
Python migration draft for `src/bridge/bridgeApi.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

class BridgeFatalError:
    """Migrated placeholder for TypeScript class `BridgeFatalError`."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs

async def createBridgeApiClient(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `createBridgeApiClient`."""
    raise NotImplementedError(
        "bridge.bridgeApi.createBridgeApiClient still needs business-logic migration"
    )

async def isExpiredErrorType(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isExpiredErrorType`."""
    raise NotImplementedError(
        "bridge.bridgeApi.isExpiredErrorType still needs business-logic migration"
    )

async def isSuppressible403(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isSuppressible403`."""
    raise NotImplementedError(
        "bridge.bridgeApi.isSuppressible403 still needs business-logic migration"
    )

async def validateBridgeId(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `validateBridgeId`."""
    raise NotImplementedError(
        "bridge.bridgeApi.validateBridgeId still needs business-logic migration"
    )
