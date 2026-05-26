"""Pure Python fuzzy file index compatible with the TS native shim."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import PurePath
from typing import Iterable

TOP_LEVEL_CACHE_LIMIT = 100
CHUNK_MS = 4


@dataclass(frozen=True)
class SearchResult:
    path: str
    score: float

    def as_dict(self) -> dict[str, str | float]:
        return {"path": self.path, "score": self.score}


def _dedupe(paths: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in paths:
        path = str(raw)
        if path and path not in seen:
            seen.add(path)
            out.append(path)
    return out


def _top_level_entries(paths: list[str], limit: int = TOP_LEVEL_CACHE_LIMIT) -> list[SearchResult]:
    segments: set[str] = set()
    for path in paths:
        normalized = path.replace("\\", "/")
        segment = normalized.split("/", 1)[0]
        if segment:
            segments.add(segment)
            if len(segments) >= limit:
                break
    return [SearchResult(path=s, score=0.0) for s in sorted(segments, key=lambda s: (len(s), s))[:limit]]


def _fuzzy_score(path: str, query: str) -> int | None:
    if not query:
        return 0

    case_sensitive = query != query.lower()
    haystack = path if case_sensitive else path.lower()
    needle = query if case_sensitive else query.lower()

    positions: list[int] = []
    start = 0
    for ch in needle:
        pos = haystack.find(ch, start)
        if pos < 0:
            return None
        positions.append(pos)
        start = pos + 1

    score = len(needle) * 16
    previous = -1
    for index, pos in enumerate(positions):
        if index == 0 and pos == 0:
            score += 8
        elif pos > 0 and path[pos - 1] in "/\\-_. ":
            score += 8
        elif pos > 0 and path[pos - 1].islower() and path[pos].isupper():
            score += 6
        if previous >= 0:
            gap = pos - previous - 1
            score += 4 if gap == 0 else -(3 + gap)
        previous = pos
    score += max(0, 32 - (len(path) // 4))
    if "test" in path.lower():
        score -= 1
    return score


class FileIndex:
    """Small fuzzy matcher preserving ``loadFromFileList`` and ``search``."""

    def __init__(self) -> None:
        self.paths: list[str] = []
        self._top_level_cache: list[SearchResult] = []

    def loadFromFileList(self, fileList: Iterable[str]) -> None:
        self.paths = _dedupe(fileList)
        self._top_level_cache = _top_level_entries(self.paths)

    def load_from_file_list(self, file_list: Iterable[str]) -> None:
        self.loadFromFileList(file_list)

    def loadFromFileListAsync(self, fileList: Iterable[str]) -> dict[str, asyncio.Task[None]]:
        async def build() -> None:
            self.loadFromFileList(fileList)
            await yieldToEventLoop()

        task = asyncio.create_task(build())
        return {"queryable": task, "done": task}

    def search(self, query: str, limit: int) -> list[dict[str, str | float]]:
        if limit <= 0:
            return []
        if not query:
            return [r.as_dict() for r in self._top_level_cache[:limit]]

        ranked: list[tuple[int, str]] = []
        for path in self.paths:
            score = _fuzzy_score(path, query)
            if score is not None:
                ranked.append((score, path))
        ranked.sort(key=lambda item: (-item[0], len(PurePath(item[1]).parts), item[1]))

        count = min(limit, len(ranked))
        denom = max(count, 1)
        results: list[dict[str, str | float]] = []
        for index, (_, path) in enumerate(ranked[:limit]):
            position_score = index / denom
            if "test" in path.lower():
                position_score = min(position_score * 1.05, 1.0)
            results.append({"path": path, "score": position_score})
        return results


async def yieldToEventLoop() -> None:
    await asyncio.sleep(0)


__all__ = ["CHUNK_MS", "FileIndex", "SearchResult", "yieldToEventLoop"]
