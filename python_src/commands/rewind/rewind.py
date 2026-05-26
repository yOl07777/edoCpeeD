"""Local `/rewind` command shim."""

from __future__ import annotations

from typing import Any

from python_src.history import removeLastFromHistory
from python_src.session_store import SESSION_STATE


async def call(onDone: Any = None, *_args: Any, **_kwargs: Any) -> dict[str, Any] | None:
    removed = SESSION_STATE.messages.pop() if SESSION_STATE.messages else None
    removeLastFromHistory()
    message = "Rewound the last in-memory session message." if removed else "Nothing to rewind."
    if callable(onDone):
        try:
            onDone(message, {"display": "system"})
        except TypeError:
            onDone(message)
        return None
    return {"type": "text", "value": message, "removed": removed}
