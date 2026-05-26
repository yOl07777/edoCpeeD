"""Local `/share` command shim."""

from __future__ import annotations

from typing import Any

from python_src.session_store import SESSION_STATE


def buildSharePayload(include_messages: bool = True) -> dict[str, Any]:
    messages = list(SESSION_STATE.messages) if include_messages else []
    return {
        "type": "share_payload",
        "provider": "deepseek",
        "messageCount": len(SESSION_STATE.messages),
        "messages": messages,
    }


def formatSharePayload(payload: dict[str, Any]) -> str:
    return (
        "Local share payload prepared. "
        f"{payload['messageCount']} in-memory message(s) are available for export."
    )


async def call(onDone: Any = None, _context: Any = None, args: str = "") -> dict[str, Any] | None:
    include_messages = "metadata" not in (args or "").lower()
    payload = buildSharePayload(include_messages)
    message = formatSharePayload(payload)
    if callable(onDone):
        try:
            onDone(message, {"display": "system"})
        except TypeError:
            onDone(message)
        return None
    return {"type": "text", "value": message, "payload": payload}


share = {
    "type": "local",
    "name": "share",
    "description": "Prepare a local share payload for the current session",
    "supportsNonInteractive": True,
    "call": call,
}

default = share

__all__ = ["buildSharePayload", "call", "default", "formatSharePayload", "share"]
