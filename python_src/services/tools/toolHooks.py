from __future__ import annotations

from typing import Any


async def resolveHookPermissionDecision(decisions: list[dict[str, Any]] | dict[str, Any] | None) -> dict[str, Any]:
    if decisions is None:
        return {"behavior": "ask", "allowed": False, "reason": "no_decision"}
    items = [decisions] if isinstance(decisions, dict) else decisions
    for decision in items:
        if decision.get("behavior") == "deny" or decision.get("allowed") is False and decision.get("reason"):
            return {"behavior": "deny", "allowed": False, "reason": decision.get("reason")}
    if any(decision.get("behavior") == "allow" or decision.get("allowed") is True for decision in items):
        return {"behavior": "allow", "allowed": True, "reason": None}
    return {"behavior": "ask", "allowed": False, "reason": "requires_confirmation"}
