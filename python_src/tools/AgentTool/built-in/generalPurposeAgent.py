"""Built-in general purpose agent definition."""

from __future__ import annotations

from typing import Any

GENERAL_PURPOSE_AGENT: dict[str, Any] = {
    "agentType": "general-purpose",
    "name": "General purpose",
    "description": "Handles broad local coding and research tasks.",
    "source": "built-in",
}

__all__ = ["GENERAL_PURPOSE_AGENT"]
