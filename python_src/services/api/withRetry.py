"""
Python migration draft for `src/services/api/withRetry.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

BASE_DELAY_MS: Any = None

class CannotRetryError:
    """Migrated placeholder for TypeScript class `CannotRetryError`."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs

class FallbackTriggeredError:
    """Migrated placeholder for TypeScript class `FallbackTriggeredError`."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs

async def getDefaultMaxRetries(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getDefaultMaxRetries`."""
    raise NotImplementedError(
        "services.api.withRetry.getDefaultMaxRetries still needs business-logic migration"
    )

async def getRetryDelay(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getRetryDelay`."""
    raise NotImplementedError(
        "services.api.withRetry.getRetryDelay still needs business-logic migration"
    )

async def is529Error(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `is529Error`."""
    raise NotImplementedError(
        "services.api.withRetry.is529Error still needs business-logic migration"
    )

async def parseMaxTokensContextOverflowError(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `parseMaxTokensContextOverflowError`."""
    raise NotImplementedError(
        "services.api.withRetry.parseMaxTokensContextOverflowError still needs business-logic migration"
    )
