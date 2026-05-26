"""Built-in explore agent definition."""

from __future__ import annotations

from typing import Any

EXPLORE_AGENT_MIN_QUERIES = 2
EXPLORE_AGENT: dict[str, Any] = {
    "agentType": "explore",
    "name": "Explore",
    "description": "Investigates the workspace before implementation.",
    "source": "built-in",
}

__all__ = ["EXPLORE_AGENT", "EXPLORE_AGENT_MIN_QUERIES"]
