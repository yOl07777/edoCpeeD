"""
Python migration draft for `src/assistant/sessionHistory.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

HISTORY_PAGE_SIZE: Any = None

async def createHistoryAuthCtx(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `createHistoryAuthCtx`."""
    raise NotImplementedError(
        "assistant.sessionHistory.createHistoryAuthCtx still needs business-logic migration"
    )

async def fetchLatestEvents(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `fetchLatestEvents`."""
    raise NotImplementedError(
        "assistant.sessionHistory.fetchLatestEvents still needs business-logic migration"
    )

async def fetchOlderEvents(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `fetchOlderEvents`."""
    raise NotImplementedError(
        "assistant.sessionHistory.fetchOlderEvents still needs business-logic migration"
    )
