"""
Python migration draft for `src/context.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

getGitStatus: Any = None
getSystemContext: Any = None
getUserContext: Any = None

async def getSystemPromptInjection(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getSystemPromptInjection`."""
    raise NotImplementedError(
        "context.getSystemPromptInjection still needs business-logic migration"
    )

async def setSystemPromptInjection(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `setSystemPromptInjection`."""
    raise NotImplementedError(
        "context.setSystemPromptInjection still needs business-logic migration"
    )
