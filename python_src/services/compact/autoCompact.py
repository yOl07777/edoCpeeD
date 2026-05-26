"""Auto-compaction threshold and execution helpers."""

from __future__ import annotations

import os
from typing import Any

from python_src.services.compact.compact import ERROR_MESSAGE_USER_ABORT, compactConversation
from python_src.services.compact.microCompact import estimateMessageTokens
from python_src.services.compact.postCompactCleanup import runPostCompactCleanup
from python_src.services.compact.sessionMemoryCompact import trySessionMemoryCompaction


MAX_OUTPUT_TOKENS_FOR_SUMMARY = 20_000
AUTOCOMPACT_BUFFER_TOKENS = 13_000
WARNING_THRESHOLD_BUFFER_TOKENS = 20_000
ERROR_THRESHOLD_BUFFER_TOKENS = 20_000
MANUAL_COMPACT_BUFFER_TOKENS = 3_000
MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3

_CONTEXT_WINDOWS = {
    "deepseek-chat": 64_000,
    "deepseek-coder": 128_000,
    "deepseek-reasoner": 64_000,
    "deepseek-v4-flash": 128_000,
    "deepseek-v4-pro": 128_000,
}


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, ""))
    except ValueError:
        return default
    return value if value > 0 else default


async def getEffectiveContextWindowSize(model: str, *_: Any, **__: Any) -> int:
    context_window = _CONTEXT_WINDOWS.get(model, _CONTEXT_WINDOWS["deepseek-chat"])
    override = os.getenv("DEEPSEEK_CODE_AUTO_COMPACT_WINDOW") or os.getenv("CLAUDE_CODE_AUTO_COMPACT_WINDOW")
    if override:
        try:
            parsed = int(override)
        except ValueError:
            parsed = 0
        if parsed > 0:
            context_window = min(context_window, parsed)
    reserved = min(MAX_OUTPUT_TOKENS_FOR_SUMMARY, _int_env("DEEPSEEK_MAX_OUTPUT_TOKENS", MAX_OUTPUT_TOKENS_FOR_SUMMARY))
    return max(1, context_window - reserved)


async def getAutoCompactThreshold(model: str, *_: Any, **__: Any) -> int:
    effective = await getEffectiveContextWindowSize(model)
    threshold = effective - AUTOCOMPACT_BUFFER_TOKENS
    override = os.getenv("DEEPSEEK_AUTOCOMPACT_PCT_OVERRIDE") or os.getenv("CLAUDE_AUTOCOMPACT_PCT_OVERRIDE")
    if override:
        try:
            pct = float(override)
        except ValueError:
            pct = 0
        if 0 < pct <= 100:
            threshold = min(int(effective * (pct / 100)), threshold)
    return max(1, threshold)


async def isAutoCompactEnabled(*_: Any, **__: Any) -> bool:
    if _truthy(os.getenv("DISABLE_COMPACT")) or _truthy(os.getenv("DISABLE_AUTO_COMPACT")):
        return False
    if os.getenv("DEEPSEEK_AUTO_COMPACT_ENABLED") is not None:
        return _truthy(os.getenv("DEEPSEEK_AUTO_COMPACT_ENABLED"))
    return True


async def calculateTokenWarningState(tokenUsage: int, model: str, *_: Any, **__: Any) -> dict[str, Any]:
    auto_threshold = await getAutoCompactThreshold(model)
    threshold = auto_threshold if await isAutoCompactEnabled() else await getEffectiveContextWindowSize(model)
    percent_left = max(0, round(((threshold - tokenUsage) / threshold) * 100))
    warning_threshold = threshold - WARNING_THRESHOLD_BUFFER_TOKENS
    error_threshold = threshold - ERROR_THRESHOLD_BUFFER_TOKENS
    blocking_limit = _int_env(
        "DEEPSEEK_CODE_BLOCKING_LIMIT_OVERRIDE",
        (await getEffectiveContextWindowSize(model)) - MANUAL_COMPACT_BUFFER_TOKENS,
    )
    return {
        "percentLeft": percent_left,
        "isAboveWarningThreshold": tokenUsage >= warning_threshold,
        "isAboveErrorThreshold": tokenUsage >= error_threshold,
        "isAboveAutoCompactThreshold": await isAutoCompactEnabled() and tokenUsage >= auto_threshold,
        "isAtBlockingLimit": tokenUsage >= blocking_limit,
    }


async def shouldAutoCompact(
    messages: list[dict[str, Any]],
    model: str,
    querySource: str | None = None,
    snipTokensFreed: int = 0,
    *_: Any,
    **__: Any,
) -> bool:
    if querySource in {"session_memory", "compact", "marble_origami"}:
        return False
    if not await isAutoCompactEnabled():
        return False
    token_count = max(0, await estimateMessageTokens(messages) - int(snipTokensFreed or 0))
    state = await calculateTokenWarningState(token_count, model)
    return bool(state["isAboveAutoCompactThreshold"])


async def autoCompactIfNeeded(
    messages: list[dict[str, Any]],
    toolUseContext: dict[str, Any] | None = None,
    cacheSafeParams: dict[str, Any] | None = None,
    querySource: str | None = None,
    tracking: dict[str, Any] | None = None,
    snipTokensFreed: int | None = None,
    *_: Any,
    **__: Any,
) -> dict[str, Any]:
    if _truthy(os.getenv("DISABLE_COMPACT")):
        return {"wasCompacted": False}
    if tracking and int(tracking.get("consecutiveFailures") or 0) >= MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES:
        return {"wasCompacted": False}

    context = toolUseContext or {}
    model = ((context.get("options") or {}).get("mainLoopModel")) or context.get("model") or os.getenv("DEFAULT_MODEL") or "deepseek-chat"
    if not await shouldAutoCompact(messages, model, querySource, snipTokensFreed or 0):
        return {"wasCompacted": False}

    threshold = await getAutoCompactThreshold(model)
    sm_result = await trySessionMemoryCompaction(messages, context.get("agentId"), threshold)
    if sm_result:
        await runPostCompactCleanup(querySource)
        return {"wasCompacted": True, "compactionResult": sm_result, "consecutiveFailures": 0}

    try:
        preserve_last = int((cacheSafeParams or {}).get("preserve_last", 6))
        result = await compactConversation(messages, preserve_last=preserve_last)
        if not result.get("compacted"):
            return {"wasCompacted": False, "compactionResult": result}
        await runPostCompactCleanup(querySource)
        return {"wasCompacted": True, "compactionResult": result, "consecutiveFailures": 0}
    except Exception as exc:
        if str(exc) != ERROR_MESSAGE_USER_ABORT:
            pass
        failures = int((tracking or {}).get("consecutiveFailures") or 0) + 1
        return {"wasCompacted": False, "consecutiveFailures": failures, "error": str(exc)}


__all__ = [
    "AUTOCOMPACT_BUFFER_TOKENS",
    "ERROR_THRESHOLD_BUFFER_TOKENS",
    "MANUAL_COMPACT_BUFFER_TOKENS",
    "WARNING_THRESHOLD_BUFFER_TOKENS",
    "autoCompactIfNeeded",
    "calculateTokenWarningState",
    "getAutoCompactThreshold",
    "getEffectiveContextWindowSize",
    "isAutoCompactEnabled",
    "shouldAutoCompact",
]
