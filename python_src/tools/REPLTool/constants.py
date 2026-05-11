"""
Python migration draft for `src/tools/REPLTool/constants.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

REPL_ONLY_TOOLS: Any = None
REPL_TOOL_NAME: Any = None

async def isReplModeEnabled(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isReplModeEnabled`."""
    raise NotImplementedError(
        "tools.REPLTool.constants.isReplModeEnabled still needs business-logic migration"
    )
