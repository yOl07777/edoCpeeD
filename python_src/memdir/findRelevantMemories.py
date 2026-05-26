"""Local deterministic memory relevance selection.

The TypeScript implementation used a Claude side query to choose memories.  For
the DeepSeek migration this stays local and deterministic: it scores scanned
memory headers by query overlap, type hints, and filename matches.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .memoryScan import MemoryHeader, scanMemoryFiles

MAX_RELEVANT_MEMORIES = 5
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "with",
}


@dataclass(frozen=True)
class RelevantMemory:
    path: str
    mtimeMs: float

    def to_dict(self) -> dict[str, float | str]:
        return {"path": self.path, "mtimeMs": self.mtimeMs}


def _terms(value: str) -> set[str]:
    return {term for term in re.findall(r"[\w.-]+", value.lower()) if len(term) > 2 and term not in STOPWORDS}


def _already_surfaced_contains(alreadySurfaced: Any, path: str) -> bool:
    if alreadySurfaced is None:
        return False
    try:
        return path in alreadySurfaced
    except TypeError:
        return False


def _tool_reference_penalty(memory: MemoryHeader, recent_tools: Iterable[str]) -> int:
    haystack = f"{memory.filename} {memory.description or ''}".lower()
    penalty = 0
    for tool in recent_tools:
        normalized = str(tool).lower().replace("_", "-")
        if normalized and normalized in haystack and "gotcha" not in haystack and "warning" not in haystack:
            penalty += 3
    return penalty


def _score_memory(query_terms: set[str], memory: MemoryHeader, recent_tools: Iterable[str]) -> int:
    haystack = f"{memory.filename} {memory.description or ''} {memory.type or ''}".lower()
    memory_terms = _terms(haystack)
    score = len(query_terms & memory_terms) * 3
    for term in query_terms:
        if term in haystack:
            score += 1
    if memory.type and memory.type in query_terms:
        score += 2
    if Path(memory.filename).stem.lower() in query_terms:
        score += 4
    return max(0, score - _tool_reference_penalty(memory, recent_tools))


async def findRelevantMemories(
    query: str,
    memoryDir: str | Path,
    signal: Any = None,
    recentTools: Iterable[str] | None = None,
    alreadySurfaced: Any = None,
    *_args: Any,
    **_kwargs: Any,
) -> list[RelevantMemory]:
    """Return up to five memory files relevant to a query."""

    if getattr(signal, "aborted", False):
        return []
    memories = [
        memory
        for memory in await scanMemoryFiles(memoryDir)
        if not _already_surfaced_contains(alreadySurfaced, memory.filePath)
    ]
    if not memories:
        return []

    query_terms = _terms(query)
    recent_tools = list(recentTools or [])
    scored = [(_score_memory(query_terms, memory, recent_tools), memory) for memory in memories]
    selected = [
        memory
        for score, memory in sorted(scored, key=lambda item: (item[0], item[1].mtimeMs), reverse=True)
        if score > 0
    ][:MAX_RELEVANT_MEMORIES]
    return [RelevantMemory(path=memory.filePath, mtimeMs=memory.mtimeMs) for memory in selected]


__all__ = ["RelevantMemory", "findRelevantMemories"]
