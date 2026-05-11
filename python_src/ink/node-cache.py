"""
Python migration draft for `src/ink/node-cache.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

nodeCache: Any = None
pendingClears: Any = None

async def addPendingClear(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `addPendingClear`."""
    raise NotImplementedError(
        "ink.node-cache.addPendingClear still needs business-logic migration"
    )

async def consumeAbsoluteRemovedFlag(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `consumeAbsoluteRemovedFlag`."""
    raise NotImplementedError(
        "ink.node-cache.consumeAbsoluteRemovedFlag still needs business-logic migration"
    )
