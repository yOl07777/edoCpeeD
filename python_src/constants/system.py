"""
Python migration draft for `src/constants/system.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

CLI_SYSPROMPT_PREFIXES: Any = None

async def getAttributionHeader(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getAttributionHeader`."""
    raise NotImplementedError(
        "constants.system.getAttributionHeader still needs business-logic migration"
    )

async def getCLISyspromptPrefix(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getCLISyspromptPrefix`."""
    raise NotImplementedError(
        "constants.system.getCLISyspromptPrefix still needs business-logic migration"
    )
