"""
Python migration draft for `src/constants/product.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

CLAUDE_AI_BASE_URL: Any = None
CLAUDE_AI_LOCAL_BASE_URL: Any = None
CLAUDE_AI_STAGING_BASE_URL: Any = None
PRODUCT_URL: Any = None

async def getClaudeAiBaseUrl(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getClaudeAiBaseUrl`."""
    raise NotImplementedError(
        "constants.product.getClaudeAiBaseUrl still needs business-logic migration"
    )

async def getRemoteSessionUrl(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getRemoteSessionUrl`."""
    raise NotImplementedError(
        "constants.product.getRemoteSessionUrl still needs business-logic migration"
    )

async def isRemoteSessionLocal(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isRemoteSessionLocal`."""
    raise NotImplementedError(
        "constants.product.isRemoteSessionLocal still needs business-logic migration"
    )

async def isRemoteSessionStaging(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isRemoteSessionStaging`."""
    raise NotImplementedError(
        "constants.product.isRemoteSessionStaging still needs business-logic migration"
    )
