"""
Python migration draft for `src/services/mcp/claudeai.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

fetchClaudeAIMcpConfigsIfEligible: Any = None

async def clearClaudeAIMcpConfigsCache(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `clearClaudeAIMcpConfigsCache`."""
    raise NotImplementedError(
        "services.mcp.claudeai.clearClaudeAIMcpConfigsCache still needs business-logic migration"
    )

async def hasClaudeAiMcpEverConnected(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `hasClaudeAiMcpEverConnected`."""
    raise NotImplementedError(
        "services.mcp.claudeai.hasClaudeAiMcpEverConnected still needs business-logic migration"
    )

async def markClaudeAiMcpConnected(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `markClaudeAiMcpConnected`."""
    raise NotImplementedError(
        "services.mcp.claudeai.markClaudeAiMcpConnected still needs business-logic migration"
    )
