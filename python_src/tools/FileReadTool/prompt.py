"""
Python migration draft for `src/tools/FileReadTool/prompt.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

DESCRIPTION: Any = None
FILE_READ_TOOL_NAME: Any = None
FILE_UNCHANGED_STUB: Any = None
LINE_FORMAT_INSTRUCTION: Any = None
MAX_LINES_TO_READ: Any = None
OFFSET_INSTRUCTION_DEFAULT: Any = None
OFFSET_INSTRUCTION_TARGETED: Any = None

async def renderPromptTemplate(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `renderPromptTemplate`."""
    raise NotImplementedError(
        "tools.FileReadTool.prompt.renderPromptTemplate still needs business-logic migration"
    )
