from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


_TIP_HISTORY: dict[str, dict[str, Any]] = {}
_SESSION_COUNTER = 0


async def recordTipShown(tip_id: str, *, session_id: str | None = None) -> dict[str, Any]:
    global _SESSION_COUNTER
    _SESSION_COUNTER += 1
    record = {
        "tip_id": tip_id,
        "session_id": session_id,
        "session_index": _SESSION_COUNTER,
        "shown_at": datetime.now(timezone.utc).isoformat(),
    }
    _TIP_HISTORY[tip_id] = record
    return dict(record)


async def getSessionsSinceLastShown(tip_id: str) -> int | None:
    record = _TIP_HISTORY.get(tip_id)
    if record is None:
        return None
    return max(0, _SESSION_COUNTER - int(record.get("session_index", 0)))
