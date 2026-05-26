"""Session-memory based compaction shim."""

from __future__ import annotations

import os
import time
import uuid
from typing import Any

from python_src.services.SessionMemory.prompts import isSessionMemoryEmpty, truncateSessionMemoryForCompact
from python_src.services.SessionMemory.sessionMemoryUtils import (
    getLastSummarizedMessageId,
    getSessionMemoryContent,
    waitForSessionMemoryExtraction,
)
from python_src.services.compact.microCompact import estimateMessageTokens
from python_src.services.compact.prompt import getCompactUserSummaryMessage


DEFAULT_SM_COMPACT_CONFIG = {"minTokens": 10_000, "minTextBlockMessages": 5, "maxTokens": 40_000}
_sm_config = dict(DEFAULT_SM_COMPACT_CONFIG)
_config_initialized = False


def setSessionMemoryCompactConfig(config: dict[str, Any] | None = None, *_: Any, **__: Any) -> None:
    if config:
        _sm_config.update({k: v for k, v in config.items() if v is not None})


def getSessionMemoryCompactConfig(*_: Any, **__: Any) -> dict[str, Any]:
    return dict(_sm_config)


def resetSessionMemoryCompactConfig(*_: Any, **__: Any) -> None:
    global _sm_config, _config_initialized
    _sm_config = dict(DEFAULT_SM_COMPACT_CONFIG)
    _config_initialized = False


def _content_blocks(message: dict[str, Any]) -> list[Any]:
    content = (message.get("message") or {}).get("content", message.get("content"))
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return content if isinstance(content, list) else []


def hasTextBlocks(message: dict[str, Any], *_: Any, **__: Any) -> bool:
    for block in _content_blocks(message):
        if isinstance(block, dict) and block.get("type") == "text" and str(block.get("text") or ""):
            return True
    return False


def _tool_result_ids(message: dict[str, Any]) -> list[str]:
    if message.get("type") != "user":
        return []
    return [
        block["tool_use_id"]
        for block in _content_blocks(message)
        if isinstance(block, dict) and block.get("type") == "tool_result" and isinstance(block.get("tool_use_id"), str)
    ]


def _tool_use_ids(message: dict[str, Any]) -> set[str]:
    if message.get("type") != "assistant":
        return set()
    return {
        block["id"]
        for block in _content_blocks(message)
        if isinstance(block, dict) and block.get("type") in {"tool_use", "tool_call"} and isinstance(block.get("id"), str)
    }


def _message_id(message: dict[str, Any]) -> str | None:
    nested = message.get("message") if isinstance(message.get("message"), dict) else {}
    return nested.get("id") or message.get("id")


def _is_compact_boundary(message: dict[str, Any]) -> bool:
    return bool(message.get("compact_boundary") or message.get("isCompactBoundary") or message.get("type") == "compact_boundary")


def adjustIndexToPreserveAPIInvariants(messages: list[dict[str, Any]], startIndex: int, *_: Any, **__: Any) -> int:
    if startIndex <= 0 or startIndex >= len(messages):
        return startIndex
    adjusted = startIndex

    all_tool_result_ids: list[str] = []
    for msg in messages[startIndex:]:
        all_tool_result_ids.extend(_tool_result_ids(msg))
    if all_tool_result_ids:
        kept_tool_use_ids: set[str] = set()
        for msg in messages[adjusted:]:
            kept_tool_use_ids.update(_tool_use_ids(msg))
        needed = {item for item in all_tool_result_ids if item not in kept_tool_use_ids}
        for idx in range(adjusted - 1, -1, -1):
            ids = _tool_use_ids(messages[idx])
            if ids & needed:
                adjusted = idx
                needed -= ids
            if not needed:
                break

    kept_message_ids = {
        mid
        for mid in (_message_id(msg) for msg in messages[adjusted:] if msg.get("type") == "assistant")
        if mid
    }
    for idx in range(adjusted - 1, -1, -1):
        if messages[idx].get("type") == "assistant" and _message_id(messages[idx]) in kept_message_ids:
            adjusted = idx
    return adjusted


async def calculateMessagesToKeepIndex(messages: list[dict[str, Any]], lastSummarizedIndex: int, *_: Any, **__: Any) -> int:
    if not messages:
        return 0
    config = getSessionMemoryCompactConfig()
    start = lastSummarizedIndex + 1 if lastSummarizedIndex >= 0 else len(messages)

    async def segment_stats(index: int) -> tuple[int, int]:
        total = 0
        text_count = 0
        for msg in messages[index:]:
            total += await estimateMessageTokens([msg])
            if hasTextBlocks(msg):
                text_count += 1
        return total, text_count

    total_tokens, text_count = await segment_stats(start)
    if total_tokens >= int(config["maxTokens"]) or (
        total_tokens >= int(config["minTokens"]) and text_count >= int(config["minTextBlockMessages"])
    ):
        return adjustIndexToPreserveAPIInvariants(messages, start)

    boundary_idx = max((i for i, msg in enumerate(messages) if _is_compact_boundary(msg)), default=-1)
    floor = boundary_idx + 1 if boundary_idx >= 0 else 0
    for idx in range(start - 1, floor - 1, -1):
        msg_tokens = await estimateMessageTokens([messages[idx]])
        total_tokens += msg_tokens
        if hasTextBlocks(messages[idx]):
            text_count += 1
        start = idx
        if total_tokens >= int(config["maxTokens"]):
            break
        if total_tokens >= int(config["minTokens"]) and text_count >= int(config["minTextBlockMessages"]):
            break
    return adjustIndexToPreserveAPIInvariants(messages, start)


def shouldUseSessionMemoryCompaction(*_: Any, **__: Any) -> bool:
    if str(os.getenv("ENABLE_DEEPSEEK_CODE_SM_COMPACT") or os.getenv("ENABLE_CLAUDE_CODE_SM_COMPACT") or "").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }:
        return True
    if str(os.getenv("DISABLE_DEEPSEEK_CODE_SM_COMPACT") or os.getenv("DISABLE_CLAUDE_CODE_SM_COMPACT") or "").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }:
        return False
    return False


async def _init_config_from_env() -> None:
    global _config_initialized
    if _config_initialized:
        return
    _config_initialized = True
    updates: dict[str, int] = {}
    for env, key in [
        ("DEEPSEEK_SM_COMPACT_MIN_TOKENS", "minTokens"),
        ("DEEPSEEK_SM_COMPACT_MIN_TEXT_MESSAGES", "minTextBlockMessages"),
        ("DEEPSEEK_SM_COMPACT_MAX_TOKENS", "maxTokens"),
    ]:
        try:
            value = int(os.getenv(env, ""))
        except ValueError:
            continue
        if value > 0:
            updates[key] = value
    setSessionMemoryCompactConfig(updates)


async def trySessionMemoryCompaction(
    messages: list[dict[str, Any]],
    agentId: str | None = None,
    autoCompactThreshold: int | None = None,
    *_: Any,
    **__: Any,
) -> dict[str, Any] | None:
    if not shouldUseSessionMemoryCompaction():
        return None
    await _init_config_from_env()
    await waitForSessionMemoryExtraction()
    session_memory = await getSessionMemoryContent()
    if not session_memory or await isSessionMemoryEmpty(session_memory):
        return None

    last_id = await getLastSummarizedMessageId()
    if last_id:
        last_index = next((i for i, msg in enumerate(messages) if msg.get("uuid") == last_id), -1)
        if last_index == -1:
            return None
    else:
        last_index = len(messages) - 1

    start_index = await calculateMessagesToKeepIndex(messages, last_index)
    messages_to_keep = [msg for msg in messages[start_index:] if not _is_compact_boundary(msg)]
    truncated = await truncateSessionMemoryForCompact(session_memory)
    summary_message = await getCompactUserSummaryMessage(
        truncated,
        {"session_memory": True, "agentId": agentId} if agentId else {"session_memory": True},
    )
    if "uuid" not in summary_message:
        summary_message["uuid"] = uuid.uuid4().hex
    boundary = {
        "type": "compact_boundary",
        "uuid": uuid.uuid4().hex,
        "timestamp": datetime_ms(),
        "compactMetadata": {"mode": "session_memory", "preservedFromIndex": start_index},
    }
    post_messages = [boundary, summary_message, *messages_to_keep]
    post_tokens = await estimateMessageTokens(post_messages)
    if autoCompactThreshold is not None and post_tokens >= autoCompactThreshold:
        return None
    return {
        "boundaryMarker": boundary,
        "summaryMessages": [summary_message],
        "attachments": [],
        "hookResults": [],
        "messagesToKeep": messages_to_keep,
        "preCompactTokenCount": await estimateMessageTokens(messages),
        "postCompactTokenCount": post_tokens,
        "truePostCompactTokenCount": post_tokens,
        "messages": post_messages,
    }


def datetime_ms() -> int:
    return int(time.time() * 1000)


__all__ = [
    "DEFAULT_SM_COMPACT_CONFIG",
    "adjustIndexToPreserveAPIInvariants",
    "calculateMessagesToKeepIndex",
    "getSessionMemoryCompactConfig",
    "hasTextBlocks",
    "resetSessionMemoryCompactConfig",
    "setSessionMemoryCompactConfig",
    "shouldUseSessionMemoryCompaction",
    "trySessionMemoryCompaction",
]
