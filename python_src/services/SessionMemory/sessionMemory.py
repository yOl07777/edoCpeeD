from __future__ import annotations

import re
from typing import Any

from python_src.services.SessionMemory.prompts import truncateSessionMemoryForCompact
from python_src.services.SessionMemory.sessionMemoryUtils import (
    getSessionMemoryContent,
    hasMetInitializationThreshold,
    hasMetUpdateThreshold,
    isSessionMemoryInitialized,
    markExtractionCompleted,
    markExtractionStarted,
    markSessionMemoryInitialized,
    setLastSummarizedMessageId,
)


async def createMemoryFileCanUseTool(allowed: bool = True) -> dict[str, bool]:
    return {"can_use_tool": allowed}


def _extract_facts(messages: list[dict[str, Any]]) -> list[str]:
    facts: list[str] = []
    patterns = [
        re.compile(r"\b(remember|note|important|decision|todo|task)\b", re.IGNORECASE),
        re.compile(r"\b(file|changed|created|updated|test|passed|failed)\b", re.IGNORECASE),
    ]
    for message in messages:
        text = str(message.get("content", "")).strip().replace("\n", " ")
        if text and any(pattern.search(text) for pattern in patterns):
            facts.append(f"- {message.get('role', 'user')}: {text[:500]}")
    return facts


async def manuallyExtractSessionMemory(messages: list[dict[str, Any]], *, existing: str | None = None) -> dict[str, Any]:
    await markExtractionStarted()
    facts = _extract_facts(messages)
    content = "\n".join(part for part in [existing or await getSessionMemoryContent(), *facts] if part).strip()
    content = await truncateSessionMemoryForCompact(content)
    last_id = str(messages[-1].get("id")) if messages and messages[-1].get("id") else None
    await markExtractionCompleted(content, last_id)
    return {"content": content, "facts": facts, "last_message_id": last_id}


async def initSessionMemory(messages: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    result = await manuallyExtractSessionMemory(messages or [])
    await markSessionMemoryInitialized(result["content"])
    return {"initialized": True, **result}


async def shouldExtractMemory(messages: list[dict[str, Any]]) -> bool:
    if not await isSessionMemoryInitialized():
        return await hasMetInitializationThreshold(messages)
    return await hasMetUpdateThreshold(messages)


async def resetLastMemoryMessageUuid() -> None:
    await setLastSummarizedMessageId(None)
