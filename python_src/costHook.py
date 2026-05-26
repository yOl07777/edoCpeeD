"""Cost summary helpers for the Python/DeepSeek runtime."""

from __future__ import annotations

from typing import Any

from python_src import cost_tracker


async def useCostSummary(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    """Return a hook-like cost summary without depending on React."""

    text = await cost_tracker.formatTotalCost()
    return {
        "type": "cost_summary",
        "provider": "deepseek",
        "summary": text,
        "totalCostUSD": cost_tracker.getTotalCost(),
        "totalInputTokens": cost_tracker.getTotalInputTokens(),
        "totalOutputTokens": cost_tracker.getTotalOutputTokens(),
        "totalCacheReadInputTokens": cost_tracker.getTotalCacheReadInputTokens(),
        "totalCacheCreationInputTokens": cost_tracker.getTotalCacheCreationInputTokens(),
        "totalWebSearchRequests": cost_tracker.getTotalWebSearchRequests(),
        "modelUsage": cost_tracker.getModelUsage(),
    }


__all__ = ["useCostSummary"]
