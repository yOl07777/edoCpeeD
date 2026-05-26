"""Microcompact helpers for shrinking stale tool results."""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from typing import Any

from .compactWarningState import clearCompactWarningSuppression, suppressCompactWarning
from .timeBasedMCConfig import getTimeBasedMCConfig


TIME_BASED_MC_CLEARED_MESSAGE = "[Old tool result content cleared]"
IMAGE_MAX_TOKEN_SIZE = 2000
COMPACTABLE_TOOLS = {
    "Read",
    "Bash",
    "run_shell",
    "PowerShell",
    "Grep",
    "Glob",
    "WebSearch",
    "WebFetch",
    "Edit",
    "Write",
    "FileEdit",
    "FileWrite",
}

_pending_cache_edits: dict[str, Any] | None = None
_pinned_cache_edits: list[dict[str, Any]] = []


def _rough_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, math.ceil(len(text) / 4))


def _content_blocks(message: dict[str, Any]) -> list[Any]:
    raw = (message.get("message") or {}).get("content", message.get("content"))
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str):
        return [{"type": "text", "text": raw}]
    return []


def _message_type(message: dict[str, Any]) -> str | None:
    return message.get("type") or (message.get("message") or {}).get("role")


def _tool_name(block: dict[str, Any]) -> str | None:
    return block.get("name") or (block.get("function") or {}).get("name")


def _tool_id(block: dict[str, Any]) -> str | None:
    return block.get("id") or block.get("tool_call_id") or block.get("tool_use_id")


def _parse_timestamp(value: Any) -> float | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000
    except ValueError:
        return None


def _calculate_tool_result_tokens(block: dict[str, Any]) -> int:
    content = block.get("content")
    if content is None:
        return 0
    if isinstance(content, str):
        return _rough_tokens(content)
    if isinstance(content, list):
        total = 0
        for item in content:
            if not isinstance(item, dict):
                total += _rough_tokens(str(item))
            elif item.get("type") == "text":
                total += _rough_tokens(str(item.get("text") or ""))
            elif item.get("type") in {"image", "document", "image_url"}:
                total += IMAGE_MAX_TOKEN_SIZE
            else:
                total += _rough_tokens(json.dumps(item, ensure_ascii=False))
        return total
    return _rough_tokens(json.dumps(content, ensure_ascii=False))


async def estimateMessageTokens(messages: list[dict[str, Any]], *_: Any, **__: Any) -> int:
    total = 0
    for message in messages:
        if _message_type(message) not in {"user", "assistant"}:
            continue
        for block in _content_blocks(message):
            if not isinstance(block, dict):
                total += _rough_tokens(str(block))
            elif block.get("type") == "text":
                total += _rough_tokens(str(block.get("text") or ""))
            elif block.get("type") == "tool_result":
                total += _calculate_tool_result_tokens(block)
            elif block.get("type") in {"image", "document", "image_url"}:
                total += IMAGE_MAX_TOKEN_SIZE
            elif block.get("type") == "thinking":
                total += _rough_tokens(str(block.get("thinking") or ""))
            elif block.get("type") == "redacted_thinking":
                total += _rough_tokens(str(block.get("data") or ""))
            elif block.get("type") in {"tool_use", "tool_call"}:
                total += _rough_tokens((_tool_name(block) or "") + json.dumps(block.get("input") or {}, ensure_ascii=False))
            else:
                total += _rough_tokens(json.dumps(block, ensure_ascii=False))
    return math.ceil(total * 4 / 3)


def _is_main_thread_source(query_source: str | None) -> bool:
    return bool(query_source and query_source.startswith("repl_main_thread"))


async def evaluateTimeBasedTrigger(
    messages: list[dict[str, Any]],
    querySource: str | None = None,
    *_: Any,
    **__: Any,
) -> dict[str, Any] | None:
    config = await getTimeBasedMCConfig()
    if not config.get("enabled") or not _is_main_thread_source(querySource):
        return None
    last_assistant = next((m for m in reversed(messages) if _message_type(m) == "assistant"), None)
    if not last_assistant:
        return None
    timestamp_ms = _parse_timestamp(last_assistant.get("timestamp") or (last_assistant.get("message") or {}).get("timestamp"))
    if timestamp_ms is None:
        return None
    gap_minutes = (datetime.now(timezone.utc).timestamp() * 1000 - timestamp_ms) / 60_000
    if not math.isfinite(gap_minutes) or gap_minutes < int(config["gapThresholdMinutes"]):
        return None
    return {"gapMinutes": gap_minutes, "config": config}


def _collect_compactable_tool_ids(messages: list[dict[str, Any]]) -> list[str]:
    ids: list[str] = []
    for message in messages:
        if _message_type(message) != "assistant":
            continue
        for block in _content_blocks(message):
            if isinstance(block, dict) and block.get("type") in {"tool_use", "tool_call"}:
                name = _tool_name(block)
                tool_id = _tool_id(block)
                if name in COMPACTABLE_TOOLS and tool_id:
                    ids.append(tool_id)
    return ids


async def _maybe_time_based_microcompact(
    messages: list[dict[str, Any]],
    querySource: str | None,
) -> dict[str, Any] | None:
    trigger = await evaluateTimeBasedTrigger(messages, querySource)
    if not trigger:
        return None
    config = trigger["config"]
    compactable_ids = _collect_compactable_tool_ids(messages)
    keep_recent = max(1, int(config.get("keepRecent") or 1))
    keep_set = set(compactable_ids[-keep_recent:])
    clear_set = {tool_id for tool_id in compactable_ids if tool_id not in keep_set}
    if not clear_set:
        return None

    tokens_saved = 0
    result: list[dict[str, Any]] = []
    for message in messages:
        if _message_type(message) != "user":
            result.append(message)
            continue
        content = _content_blocks(message)
        if not content:
            result.append(message)
            continue
        touched = False
        new_content: list[Any] = []
        for block in content:
            if (
                isinstance(block, dict)
                and block.get("type") == "tool_result"
                and block.get("tool_use_id") in clear_set
                and block.get("content") != TIME_BASED_MC_CLEARED_MESSAGE
            ):
                tokens_saved += _calculate_tool_result_tokens(block)
                new_block = dict(block)
                new_block["content"] = TIME_BASED_MC_CLEARED_MESSAGE
                new_content.append(new_block)
                touched = True
            else:
                new_content.append(block)
        if not touched:
            result.append(message)
            continue
        next_message = dict(message)
        nested = dict(message.get("message") or {})
        nested["content"] = new_content
        next_message["message"] = nested
        result.append(next_message)

    if tokens_saved == 0:
        return None
    await suppressCompactWarning()
    await resetMicrocompactState()
    return {
        "messages": result,
        "compactionInfo": {
            "timeBased": {
                "tokensSaved": tokens_saved,
                "toolsCleared": len(clear_set),
                "toolsKept": len(keep_set),
                "gapMinutes": trigger["gapMinutes"],
            }
        },
    }


async def microcompactMessages(
    messages: list[dict[str, Any]],
    toolUseContext: dict[str, Any] | None = None,
    querySource: str | None = None,
    *_: Any,
    **__: Any,
) -> dict[str, Any]:
    await clearCompactWarningSuppression()
    time_based = await _maybe_time_based_microcompact(messages, querySource)
    if time_based:
        return time_based
    return {"messages": messages}


async def consumePendingCacheEdits(*_: Any, **__: Any) -> dict[str, Any] | None:
    global _pending_cache_edits
    edits = _pending_cache_edits
    _pending_cache_edits = None
    return edits


async def getPinnedCacheEdits(*_: Any, **__: Any) -> list[dict[str, Any]]:
    return list(_pinned_cache_edits)


async def pinCacheEdits(userMessageIndex: int, block: dict[str, Any], *_: Any, **__: Any) -> None:
    _pinned_cache_edits.append({"userMessageIndex": userMessageIndex, "block": block})


async def markToolsSentToAPIState(*_: Any, **__: Any) -> None:
    return None


async def resetMicrocompactState(*_: Any, **__: Any) -> None:
    global _pending_cache_edits
    _pending_cache_edits = None
    _pinned_cache_edits.clear()


__all__ = [
    "TIME_BASED_MC_CLEARED_MESSAGE",
    "consumePendingCacheEdits",
    "estimateMessageTokens",
    "evaluateTimeBasedTrigger",
    "getPinnedCacheEdits",
    "markToolsSentToAPIState",
    "microcompactMessages",
    "pinCacheEdits",
    "resetMicrocompactState",
]
