"""
Python migration draft for `src/utils/mcpValidation.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

IMAGE_TOKEN_ESTIMATE: Any = None
MCP_TOKEN_COUNT_THRESHOLD_FACTOR: Any = None

async def getContentSizeEstimate(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getContentSizeEstimate`."""
    raise NotImplementedError(
        "utils.mcpValidation.getContentSizeEstimate still needs business-logic migration"
    )

async def getMaxMcpOutputTokens(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getMaxMcpOutputTokens`."""
    raise NotImplementedError(
        "utils.mcpValidation.getMaxMcpOutputTokens still needs business-logic migration"
    )

async def mcpContentNeedsTruncation(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `mcpContentNeedsTruncation`."""
    raise NotImplementedError(
        "utils.mcpValidation.mcpContentNeedsTruncation still needs business-logic migration"
    )

async def truncateMcpContent(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `truncateMcpContent`."""
    raise NotImplementedError(
        "utils.mcpValidation.truncateMcpContent still needs business-logic migration"
    )

async def truncateMcpContentIfNeeded(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `truncateMcpContentIfNeeded`."""
    raise NotImplementedError(
        "utils.mcpValidation.truncateMcpContentIfNeeded still needs business-logic migration"
    )
