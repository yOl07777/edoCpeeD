"""
Python migration draft for `src/utils/claudeInChrome/prompt.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

BASE_CHROME_PROMPT: Any = None
CHROME_TOOL_SEARCH_INSTRUCTIONS: Any = None
CLAUDE_IN_CHROME_SKILL_HINT: Any = None
CLAUDE_IN_CHROME_SKILL_HINT_WITH_WEBBROWSER: Any = None

async def getChromeSystemPrompt(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getChromeSystemPrompt`."""
    raise NotImplementedError(
        "utils.claudeInChrome.prompt.getChromeSystemPrompt still needs business-logic migration"
    )
