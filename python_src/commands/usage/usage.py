"""Local `/usage` command shim."""

from __future__ import annotations

from typing import Any

from python_src.bootstrap import state as bootstrap_state


def getUsageSummary() -> dict[str, Any]:
    return {
        "type": "usage",
        "model": bootstrap_state.getInitialMainLoopModel(),
        "inputTokens": bootstrap_state.getTotalInputTokens() or 0,
        "outputTokens": bootstrap_state.getTotalOutputTokens() or 0,
        "cacheCreationInputTokens": bootstrap_state.getTotalCacheCreationInputTokens() or 0,
        "cacheReadInputTokens": bootstrap_state.getTotalCacheReadInputTokens() or 0,
        "webSearchRequests": bootstrap_state.getTotalWebSearchRequests() or 0,
        "costUSD": bootstrap_state.getTotalCostUSD() or 0.0,
        "modelUsage": bootstrap_state.getModelUsage() or {},
    }


def formatUsageSummary(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"Model: {summary['model']}",
            f"Input tokens: {summary['inputTokens']}",
            f"Output tokens: {summary['outputTokens']}",
            f"Cache creation tokens: {summary['cacheCreationInputTokens']}",
            f"Cache read tokens: {summary['cacheReadInputTokens']}",
            f"Web search requests: {summary['webSearchRequests']}",
            f"Estimated cost: ${float(summary['costUSD']):.6f}",
        ]
    )


async def call(onDone: Any = None, *_args: Any, **_kwargs: Any) -> dict[str, Any] | None:
    summary = getUsageSummary()
    message = formatUsageSummary(summary)
    if callable(onDone):
        try:
            onDone(message, {"display": "system"})
        except TypeError:
            onDone(message)
        return None
    return {"type": "text", "value": message, "usage": summary}
