"""Built-in guide agent definition."""

from __future__ import annotations

from typing import Any

CLAUDE_CODE_GUIDE_AGENT_TYPE = "claude-code-guide"
CLAUDE_CODE_GUIDE_AGENT: dict[str, Any] = {
    "agentType": CLAUDE_CODE_GUIDE_AGENT_TYPE,
    "name": "DeepSeek Code guide",
    "description": "Guides Claude Code compatibility migration work.",
    "source": "built-in",
}

__all__ = ["CLAUDE_CODE_GUIDE_AGENT", "CLAUDE_CODE_GUIDE_AGENT_TYPE"]
