"""
Python migration draft for `src/utils/settings/toolValidationConfig.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

TOOL_VALIDATION_CONFIG: Any = None

async def getCustomValidation(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getCustomValidation`."""
    raise NotImplementedError(
        "utils.settings.toolValidationConfig.getCustomValidation still needs business-logic migration"
    )

async def isBashPrefixTool(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isBashPrefixTool`."""
    raise NotImplementedError(
        "utils.settings.toolValidationConfig.isBashPrefixTool still needs business-logic migration"
    )

async def isFilePatternTool(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isFilePatternTool`."""
    raise NotImplementedError(
        "utils.settings.toolValidationConfig.isFilePatternTool still needs business-logic migration"
    )
