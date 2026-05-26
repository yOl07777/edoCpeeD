from __future__ import annotations

import os
import uuid
from typing import Any


_SPECULATIONS: dict[str, dict[str, Any]] = {}


async def isSpeculationEnabled() -> bool:
    return os.getenv("DEEPSEEK_PROMPT_SPECULATION", "1").lower() not in {"0", "false", "no"}


async def prepareMessagesForInjection(messages: list[dict[str, Any]], suggestion: str) -> list[dict[str, Any]]:
    return [*messages, {"role": "assistant", "content": suggestion, "speculative": True}]


async def startSpeculation(suggestion: str, *, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    item = {"id": f"spec_{uuid.uuid4().hex[:8]}", "suggestion": suggestion, "metadata": metadata or {}, "status": "pending"}
    _SPECULATIONS[item["id"]] = item
    return dict(item)


async def acceptSpeculation(speculation_id: str) -> dict[str, Any] | None:
    item = _SPECULATIONS.get(speculation_id)
    if item:
        item["status"] = "accepted"
    return dict(item) if item else None


async def abortSpeculation(speculation_id: str | None = None) -> dict[str, Any]:
    if speculation_id:
        item = _SPECULATIONS.get(speculation_id)
        if item:
            item["status"] = "aborted"
        return dict(item) if item else {"status": "missing"}
    for item in _SPECULATIONS.values():
        item["status"] = "aborted"
    return {"status": "aborted", "count": len(_SPECULATIONS)}


async def handleSpeculationAccept(speculation_id: str) -> dict[str, Any] | None:
    return await acceptSpeculation(speculation_id)
