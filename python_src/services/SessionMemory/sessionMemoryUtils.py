from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any


DEFAULT_SESSION_MEMORY_CONFIG = {
    "enabled": True,
    "initialization_threshold": 6,
    "update_threshold": 4,
    "max_chars": 12_000,
}


@dataclass
class SessionMemoryState:
    initialized: bool = False
    extracting: bool = False
    last_summarized_message_id: str | None = None
    extraction_token_count: int = 0
    content: str = ""
    config: dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_SESSION_MEMORY_CONFIG))


STATE = SessionMemoryState()


async def resetSessionMemoryState() -> None:
    global STATE
    STATE = SessionMemoryState()


async def getSessionMemoryConfig() -> dict[str, Any]:
    return dict(STATE.config)


async def setSessionMemoryConfig(config: dict[str, Any]) -> dict[str, Any]:
    STATE.config.update(config)
    return await getSessionMemoryConfig()


async def isSessionMemoryInitialized() -> bool:
    return STATE.initialized


async def markSessionMemoryInitialized(content: str = "") -> dict[str, Any]:
    STATE.initialized = True
    if content:
        STATE.content = content
    return {"initialized": STATE.initialized, "content": STATE.content}


async def getSessionMemoryContent() -> str:
    return STATE.content


async def getLastSummarizedMessageId() -> str | None:
    return STATE.last_summarized_message_id


async def setLastSummarizedMessageId(message_id: str | None) -> str | None:
    STATE.last_summarized_message_id = message_id
    return STATE.last_summarized_message_id


async def markExtractionStarted() -> dict[str, bool]:
    STATE.extracting = True
    return {"extracting": True}


async def markExtractionCompleted(content: str | None = None, last_message_id: str | None = None) -> dict[str, Any]:
    STATE.extracting = False
    if content is not None:
        STATE.content = content
    if last_message_id is not None:
        STATE.last_summarized_message_id = last_message_id
    return {"extracting": False, "content": STATE.content, "last_summarized_message_id": STATE.last_summarized_message_id}


async def waitForSessionMemoryExtraction(timeout_seconds: float = 5.0) -> bool:
    deadline = asyncio.get_event_loop().time() + timeout_seconds
    while STATE.extracting and asyncio.get_event_loop().time() < deadline:
        await asyncio.sleep(0.01)
    return not STATE.extracting


async def recordExtractionTokenCount(count: int) -> int:
    STATE.extraction_token_count += count
    return STATE.extraction_token_count


async def hasMetInitializationThreshold(messages: list[dict[str, Any]]) -> bool:
    return len(messages) >= int(STATE.config.get("initialization_threshold", 6))


async def hasMetUpdateThreshold(messages: list[dict[str, Any]]) -> bool:
    return len(messages) >= int(STATE.config.get("update_threshold", 4))


async def getToolCallsBetweenUpdates(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [m for m in messages if m.get("tool_calls") or m.get("role") == "tool"]
