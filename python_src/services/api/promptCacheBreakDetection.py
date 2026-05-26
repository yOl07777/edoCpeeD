"""Prompt cache break detection for the DeepSeek migration.

DeepSeek does not expose Claude prompt-cache controls, but higher-level code
still benefits from detecting when a conversation state changed enough that a
cached prompt snapshot should be considered stale.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any

CACHE_TTL_1HOUR_MS = 60 * 60 * 1000

_PROMPT_STATE: dict[str, dict[str, Any]] = {}
_NOTIFICATIONS: list[dict[str, Any]] = []


def _fingerprint(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, default=str, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


async def recordPromptState(agent_id: str, prompt_state: Any, ttl_ms: int = CACHE_TTL_1HOUR_MS) -> dict[str, Any]:
    entry = {
        "agent_id": agent_id,
        "fingerprint": _fingerprint(prompt_state),
        "prompt_state": prompt_state,
        "recorded_at": time.time(),
        "expires_at": time.time() + ttl_ms / 1000,
    }
    _PROMPT_STATE[agent_id] = entry
    return dict(entry)


async def checkResponseForCacheBreak(agent_id: str, response_or_prompt_state: Any) -> dict[str, Any]:
    previous = _PROMPT_STATE.get(agent_id)
    current_fingerprint = _fingerprint(response_or_prompt_state)
    now = time.time()
    broken = previous is None or previous.get("fingerprint") != current_fingerprint or previous.get("expires_at", 0) < now
    result = {
        "agent_id": agent_id,
        "cache_broken": broken,
        "previous_fingerprint": previous.get("fingerprint") if previous else None,
        "current_fingerprint": current_fingerprint,
        "expired": bool(previous and previous.get("expires_at", 0) < now),
    }
    if broken:
        await notifyCacheDeletion(agent_id, result)
    return result


async def notifyCacheDeletion(agent_id: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    notification = {"type": "cache_deletion", "agent_id": agent_id, "details": details or {}, "timestamp": time.time()}
    _NOTIFICATIONS.append(notification)
    return notification


async def notifyCompaction(agent_id: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    notification = {"type": "compaction", "agent_id": agent_id, "details": details or {}, "timestamp": time.time()}
    _NOTIFICATIONS.append(notification)
    if agent_id in _PROMPT_STATE:
        _PROMPT_STATE.pop(agent_id, None)
    return notification


async def cleanupAgentTracking(now: float | None = None) -> dict[str, Any]:
    current = now if now is not None else time.time()
    stale = [agent_id for agent_id, entry in _PROMPT_STATE.items() if entry.get("expires_at", 0) < current]
    for agent_id in stale:
        _PROMPT_STATE.pop(agent_id, None)
    return {"removed": len(stale), "remaining": len(_PROMPT_STATE)}


async def resetPromptCacheBreakDetection() -> None:
    _PROMPT_STATE.clear()
    _NOTIFICATIONS.clear()


async def getPromptCacheBreakNotifications() -> list[dict[str, Any]]:
    return list(_NOTIFICATIONS)

