"""Local session backfill shim for the Python migration."""

from __future__ import annotations

from typing import Any, Callable

from python_src.history import makeHistoryReader
from python_src.session_store import SESSION_STATE


async def collectBackfillSummary(limit: int = 25) -> dict[str, Any]:
    history_items: list[dict[str, Any]] = []
    async for entry in makeHistoryReader():
        history_items.append(entry)
        if len(history_items) >= limit:
            break
    return {
        "provider": "deepseek",
        "historyItems": len(history_items),
        "sessionMessages": len(SESSION_STATE.messages),
        "preview": [str(item.get("display", ""))[:120] for item in history_items[:5]],
    }


async def call(onDone: Callable[[str], Any] | None = None, context: Any | None = None, args: str = "") -> dict[str, Any]:
    limit = 25
    if args.strip().isdigit():
        limit = max(1, min(200, int(args.strip())))
    summary = await collectBackfillSummary(limit)
    value = (
        "DeepSeek session backfill shim completed. "
        f"Found {summary['historyItems']} history item(s) and {summary['sessionMessages']} in-memory message(s)."
    )
    if onDone:
        onDone(value)
    return {"type": "backfill_sessions", "value": value, "summary": summary}


backfill_sessions = {
    "type": "local",
    "name": "backfill-sessions",
    "description": "Summarize local DeepSeek session history for backfill flows",
    "source": "builtin",
    "isHidden": True,
    "call": call,
}

default = backfill_sessions
