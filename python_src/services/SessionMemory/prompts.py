from __future__ import annotations

from typing import Any


DEFAULT_SESSION_MEMORY_TEMPLATE = """Session memory:
{memory}

Recent conversation:
{recent}
"""


async def isSessionMemoryEmpty(content: str | None) -> bool:
    return not (content or "").strip()


async def truncateSessionMemoryForCompact(content: str, max_chars: int = 8_000) -> str:
    text = content.strip()
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


async def loadSessionMemoryTemplate(template: str | None = None) -> str:
    return template or DEFAULT_SESSION_MEMORY_TEMPLATE


async def buildSessionMemoryUpdatePrompt(
    memory: str,
    messages: list[dict[str, Any]],
    *,
    max_recent_chars: int = 4_000,
) -> str:
    recent = "\n".join(f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages)[-max_recent_chars:]
    template = await loadSessionMemoryTemplate()
    return template.format(memory=memory or "(empty)", recent=recent)


async def loadSessionMemoryPrompt(memory: str = "", messages: list[dict[str, Any]] | None = None) -> str:
    return await buildSessionMemoryUpdatePrompt(memory, messages or [])
