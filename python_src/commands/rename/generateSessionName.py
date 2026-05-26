"""Session naming helpers."""

from __future__ import annotations

import re
from typing import Any

from python_src.session_store import SESSION_STATE


_WORD_RE = re.compile(r"[A-Za-z0-9\u4e00-\u9fff]+")


def _words(text: str) -> list[str]:
    return _WORD_RE.findall(text or "")


async def generateSessionName(prompt: str | None = None, messages: list[dict[str, Any]] | None = None, max_words: int = 6) -> str:
    source = prompt or ""
    if not source:
        for message in reversed(messages if messages is not None else SESSION_STATE.messages):
            content = str(message.get("content", ""))
            if content.strip():
                source = content
                break
    words = _words(source)
    if not words:
        return "untitled-session"
    return "-".join(words[:max(1, max_words)]).lower()[:80]
