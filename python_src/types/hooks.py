"""
Python migration draft for `src/types/hooks.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

hookJSONOutputSchema: Any = None
promptRequestSchema: Any = None
syncHookResponseSchema: Any = None

async def isAsyncHookJSONOutput(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isAsyncHookJSONOutput`."""
    raise NotImplementedError(
        "types.hooks.isAsyncHookJSONOutput still needs business-logic migration"
    )

async def isHookEvent(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isHookEvent`."""
    raise NotImplementedError(
        "types.hooks.isHookEvent still needs business-logic migration"
    )

async def isSyncHookJSONOutput(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isSyncHookJSONOutput`."""
    raise NotImplementedError(
        "types.hooks.isSyncHookJSONOutput still needs business-logic migration"
    )
