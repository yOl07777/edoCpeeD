"""
Python migration draft for `src/tools/ScheduleCronTool/prompt.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

CRON_CREATE_TOOL_NAME: Any = None
CRON_DELETE_DESCRIPTION: Any = None
CRON_DELETE_TOOL_NAME: Any = None
CRON_LIST_DESCRIPTION: Any = None
CRON_LIST_TOOL_NAME: Any = None
DEFAULT_MAX_AGE_DAYS: Any = None

async def buildCronCreateDescription(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `buildCronCreateDescription`."""
    raise NotImplementedError(
        "tools.ScheduleCronTool.prompt.buildCronCreateDescription still needs business-logic migration"
    )

async def buildCronCreatePrompt(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `buildCronCreatePrompt`."""
    raise NotImplementedError(
        "tools.ScheduleCronTool.prompt.buildCronCreatePrompt still needs business-logic migration"
    )

async def buildCronDeletePrompt(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `buildCronDeletePrompt`."""
    raise NotImplementedError(
        "tools.ScheduleCronTool.prompt.buildCronDeletePrompt still needs business-logic migration"
    )

async def buildCronListPrompt(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `buildCronListPrompt`."""
    raise NotImplementedError(
        "tools.ScheduleCronTool.prompt.buildCronListPrompt still needs business-logic migration"
    )

async def isDurableCronEnabled(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isDurableCronEnabled`."""
    raise NotImplementedError(
        "tools.ScheduleCronTool.prompt.isDurableCronEnabled still needs business-logic migration"
    )

async def isKairosCronEnabled(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isKairosCronEnabled`."""
    raise NotImplementedError(
        "tools.ScheduleCronTool.prompt.isKairosCronEnabled still needs business-logic migration"
    )
