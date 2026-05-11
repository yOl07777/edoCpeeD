"""
Python migration draft for `src/utils/shell/outputLimits.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

BASH_MAX_OUTPUT_DEFAULT: Any = None
BASH_MAX_OUTPUT_UPPER_LIMIT: Any = None

async def getMaxOutputLength(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getMaxOutputLength`."""
    raise NotImplementedError(
        "utils.shell.outputLimits.getMaxOutputLength still needs business-logic migration"
    )
