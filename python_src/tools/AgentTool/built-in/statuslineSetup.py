"""Built-in statusline setup agent definition."""

from __future__ import annotations

from typing import Any

STATUSLINE_SETUP_AGENT: dict[str, Any] = {
    "agentType": "statusline-setup",
    "name": "Statusline setup",
    "description": "Helps configure local statusline integrations.",
    "source": "built-in",
}

__all__ = ["STATUSLINE_SETUP_AGENT"]
