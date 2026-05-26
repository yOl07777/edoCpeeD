"""Query-loop token budget tracking."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from python_src.utils.tokenBudget import getBudgetContinuationMessage

COMPLETION_THRESHOLD = 0.9
DIMINISHING_THRESHOLD = 500


@dataclass
class BudgetTracker:
    continuationCount: int = 0
    lastDeltaTokens: int = 0
    lastGlobalTurnTokens: int = 0
    startedAt: float = 0.0

    def __post_init__(self) -> None:
        if not self.startedAt:
            self.startedAt = time.time() * 1000


def createBudgetTracker(*_args: Any, **_kwargs: Any) -> BudgetTracker:
    return BudgetTracker()


def checkTokenBudget(
    tracker: BudgetTracker,
    agentId: str | None,
    budget: int | None,
    globalTurnTokens: int,
    *_args: Any,
    **_kwargs: Any,
) -> dict[str, Any]:
    """Decide whether a query loop should continue to spend toward a budget."""

    if agentId or budget is None or budget <= 0:
        return {"action": "stop", "completionEvent": None}

    turn_tokens = int(globalTurnTokens)
    pct = round((turn_tokens / budget) * 100)
    delta_since_last_check = turn_tokens - tracker.lastGlobalTurnTokens
    is_diminishing = (
        tracker.continuationCount >= 3
        and delta_since_last_check < DIMINISHING_THRESHOLD
        and tracker.lastDeltaTokens < DIMINISHING_THRESHOLD
    )

    if not is_diminishing and turn_tokens < budget * COMPLETION_THRESHOLD:
        tracker.continuationCount += 1
        tracker.lastDeltaTokens = delta_since_last_check
        tracker.lastGlobalTurnTokens = turn_tokens
        return {
            "action": "continue",
            "nudgeMessage": getBudgetContinuationMessage(pct, turn_tokens, budget),
            "continuationCount": tracker.continuationCount,
            "pct": pct,
            "turnTokens": turn_tokens,
            "budget": budget,
        }

    if is_diminishing or tracker.continuationCount > 0:
        return {
            "action": "stop",
            "completionEvent": {
                "continuationCount": tracker.continuationCount,
                "pct": pct,
                "turnTokens": turn_tokens,
                "budget": budget,
                "diminishingReturns": is_diminishing,
                "durationMs": int(time.time() * 1000 - tracker.startedAt),
            },
        }

    return {"action": "stop", "completionEvent": None}


__all__ = ["BudgetTracker", "checkTokenBudget", "createBudgetTracker"]
