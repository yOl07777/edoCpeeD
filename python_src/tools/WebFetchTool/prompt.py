"""
Python migration draft for `src/tools/WebFetchTool/prompt.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

DESCRIPTION: Any = None
WEB_FETCH_TOOL_NAME: Any = None

async def makeSecondaryModelPrompt(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `makeSecondaryModelPrompt`."""
    raise NotImplementedError(
        "tools.WebFetchTool.prompt.makeSecondaryModelPrompt still needs business-logic migration"
    )
