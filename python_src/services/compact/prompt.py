from __future__ import annotations

from typing import Any


async def formatCompactSummary(summary: str, metadata: dict[str, Any] | None = None) -> str:
    lines = ["Conversation summary:", summary.strip()]
    if metadata:
        lines.append("")
        lines.append("Metadata:")
        for key, value in metadata.items():
            lines.append(f"- {key}: {value}")
    return "\n".join(lines).strip()


async def getCompactPrompt(messages: list[dict[str, Any]], *, max_chars: int = 8_000) -> str:
    text = "\n".join(f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages)
    return (
        "Summarize the following conversation for continuation. "
        "Preserve user goals, decisions, changed files, commands, test results, and blockers.\n\n"
        + text[:max_chars]
    )


async def getPartialCompactPrompt(messages: list[dict[str, Any]], *, max_chars: int = 4_000) -> str:
    return await getCompactPrompt(messages, max_chars=max_chars)


async def getCompactUserSummaryMessage(summary: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"role": "user", "content": await formatCompactSummary(summary, metadata)}
