"""
Python migration draft for `src/tools/SkillTool/prompt.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

CHARS_PER_TOKEN: Any = None
DEFAULT_CHAR_BUDGET: Any = None
MAX_LISTING_DESC_CHARS: Any = None
SKILL_BUDGET_CONTEXT_PERCENT: Any = None
getPrompt: Any = None

async def clearPromptCache(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `clearPromptCache`."""
    raise NotImplementedError(
        "tools.SkillTool.prompt.clearPromptCache still needs business-logic migration"
    )

async def formatCommandsWithinBudget(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `formatCommandsWithinBudget`."""
    raise NotImplementedError(
        "tools.SkillTool.prompt.formatCommandsWithinBudget still needs business-logic migration"
    )

async def getCharBudget(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getCharBudget`."""
    raise NotImplementedError(
        "tools.SkillTool.prompt.getCharBudget still needs business-logic migration"
    )

async def getLimitedSkillToolCommands(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getLimitedSkillToolCommands`."""
    raise NotImplementedError(
        "tools.SkillTool.prompt.getLimitedSkillToolCommands still needs business-logic migration"
    )

async def getSkillInfo(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getSkillInfo`."""
    raise NotImplementedError(
        "tools.SkillTool.prompt.getSkillInfo still needs business-logic migration"
    )

async def getSkillToolInfo(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getSkillToolInfo`."""
    raise NotImplementedError(
        "tools.SkillTool.prompt.getSkillToolInfo still needs business-logic migration"
    )
