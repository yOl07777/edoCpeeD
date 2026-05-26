"""Implementation for `/clear`, `/reset`, and `/new`."""

from __future__ import annotations

from inspect import isawaitable
from typing import Any, Awaitable, Callable

from .caches import clearSessionCaches
from .conversation import clearConversation

DoneCallback = Callable[[Any], Any | Awaitable[Any]]


async def _notify(onDone: DoneCallback | None, payload: Any) -> None:
    if onDone is None:
        return
    result = onDone(payload)
    if isawaitable(result):
        await result


async def call(
    onDone: DoneCallback | None = None,
    context: dict[str, Any] | None = None,
    args: str | None = None,
) -> dict[str, Any]:
    """Clear the migrated conversation state and transient caches."""

    preserved = []
    if isinstance(context, dict):
        preserved = list(context.get("preservedAgentIds") or [])
    conversation = clearConversation()
    caches = await clearSessionCaches(preserved)
    result = {
        "ok": True,
        "message": "Conversation history cleared.",
        "conversation": conversation,
        "caches": caches,
    }
    await _notify(onDone, result["message"])
    return result
