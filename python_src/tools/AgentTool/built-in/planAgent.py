"""Built-in plan agent definition."""

from __future__ import annotations

from typing import Any

PLAN_AGENT: dict[str, Any] = {
    "agentType": "plan",
    "name": "Plan",
    "description": "Produces implementation plans for larger changes.",
    "source": "built-in",
}

__all__ = ["PLAN_AGENT"]
