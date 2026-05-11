"""
Python migration draft for `src/constants/common.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

getSessionStartDate: Any = None

async def getLocalISODate(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getLocalISODate`."""
    raise NotImplementedError(
        "constants.common.getLocalISODate still needs business-logic migration"
    )

async def getLocalMonthYear(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getLocalMonthYear`."""
    raise NotImplementedError(
        "constants.common.getLocalMonthYear still needs business-logic migration"
    )
