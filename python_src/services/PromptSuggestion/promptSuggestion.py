from __future__ import annotations

import os
from typing import Any


SUGGESTION_LOG: list[dict[str, Any]] = []


async def shouldEnablePromptSuggestion() -> bool:
    return os.getenv("DEEPSEEK_PROMPT_SUGGESTION", "1").lower() not in {"0", "false", "no"}


async def getSuggestionSuppressReason(messages: list[dict[str, Any]] | None = None) -> str | None:
    if not await shouldEnablePromptSuggestion():
        return "disabled"
    if messages is not None and len(messages) == 0:
        return "empty_context"
    return None


async def getParentCacheSuppressReason() -> str | None:
    return None


async def getPromptVariant(messages: list[dict[str, Any]] | None = None) -> str:
    text = " ".join(str(m.get("content", "")) for m in (messages or [])[-3:]).lower()
    if "test" in text or "fail" in text:
        return "debug"
    if "refactor" in text:
        return "refactor"
    return "continue"


async def generateSuggestion(messages: list[dict[str, Any]] | None = None) -> str:
    variant = await getPromptVariant(messages)
    if variant == "debug":
        return "检查失败日志，定位最小复现，然后修复并重新运行相关测试。"
    if variant == "refactor":
        return "先确认现有行为和测试覆盖，再进行小步重构并保持接口兼容。"
    return "继续基于当前上下文推进，优先处理可验证的下一步。"


async def shouldFilterSuggestion(suggestion: str) -> bool:
    blocked = ["api key", "password", "secret"]
    return any(word in suggestion.lower() for word in blocked)


async def tryGenerateSuggestion(messages: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    reason = await getSuggestionSuppressReason(messages)
    if reason:
        await logSuggestionSuppressed(reason)
        return {"suggestion": None, "suppressed": True, "reason": reason}
    suggestion = await generateSuggestion(messages)
    if await shouldFilterSuggestion(suggestion):
        return {"suggestion": None, "suppressed": True, "reason": "filtered"}
    return {"suggestion": suggestion, "suppressed": False}


async def executePromptSuggestion(messages: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    result = await tryGenerateSuggestion(messages)
    await logSuggestionOutcome(result)
    return result


async def abortPromptSuggestion() -> dict[str, str]:
    return {"status": "aborted"}


async def logSuggestionOutcome(outcome: dict[str, Any]) -> dict[str, Any]:
    entry = {"type": "outcome", **outcome}
    SUGGESTION_LOG.append(entry)
    return entry


async def logSuggestionSuppressed(reason: str) -> dict[str, str]:
    entry = {"type": "suppressed", "reason": reason}
    SUGGESTION_LOG.append(entry)
    return entry
