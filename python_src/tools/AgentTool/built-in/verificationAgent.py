"""Built-in verification agent definition."""

from __future__ import annotations

from typing import Any

VERIFICATION_AGENT: dict[str, Any] = {
    "agentType": "verification",
    "name": "Verification",
    "description": "Checks completed work and summarizes residual risk.",
    "source": "built-in",
}

__all__ = ["VERIFICATION_AGENT"]
