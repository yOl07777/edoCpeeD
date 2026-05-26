"""Local `/stats` command shim."""

from __future__ import annotations

from typing import Any

from python_src.bootstrap import state as bootstrap_state
from python_src.session_store import SESSION_STATE
from python_src.tools.task_store import list_tasks


def getStats() -> dict[str, Any]:
    return {
        "type": "stats",
        "sessionId": bootstrap_state.getSessionId(),
        "messages": len(SESSION_STATE.messages),
        "tasks": len(list_tasks()),
        "inputTokens": bootstrap_state.getTotalInputTokens() or 0,
        "outputTokens": bootstrap_state.getTotalOutputTokens() or 0,
        "linesAdded": bootstrap_state.getTotalLinesAdded() or 0,
        "linesRemoved": bootstrap_state.getTotalLinesRemoved() or 0,
        "costUSD": bootstrap_state.getTotalCostUSD() or 0.0,
    }


def formatStats(stats: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"Session: {stats['sessionId']}",
            f"Messages: {stats['messages']}",
            f"Background tasks: {stats['tasks']}",
            f"Tokens: {stats['inputTokens']} in / {stats['outputTokens']} out",
            f"Lines changed: +{stats['linesAdded']} -{stats['linesRemoved']}",
            f"Estimated cost: ${float(stats['costUSD']):.6f}",
        ]
    )


async def call(onDone: Any = None, *_args: Any, **_kwargs: Any) -> dict[str, Any] | None:
    stats = getStats()
    message = formatStats(stats)
    if callable(onDone):
        try:
            onDone(message, {"display": "system"})
        except TypeError:
            onDone(message)
        return None
    return {"type": "text", "value": message, "stats": stats}
