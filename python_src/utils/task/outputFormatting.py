"""
Python migration draft for `src/utils/task/outputFormatting.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

TASK_MAX_OUTPUT_DEFAULT: Any = None
TASK_MAX_OUTPUT_UPPER_LIMIT: Any = None

async def formatTaskOutput(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `formatTaskOutput`."""
    raise NotImplementedError(
        "utils.task.outputFormatting.formatTaskOutput still needs business-logic migration"
    )

async def getMaxTaskOutputLength(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getMaxTaskOutputLength`."""
    raise NotImplementedError(
        "utils.task.outputFormatting.getMaxTaskOutputLength still needs business-logic migration"
    )
