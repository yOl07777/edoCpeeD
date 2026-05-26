"""Token budget parsing helpers."""

from __future__ import annotations

import re
from typing import Any

SHORTHAND_START_RE = re.compile(r"^\s*\+(\d+(?:\.\d+)?)\s*(k|m|b)\b", re.I)
SHORTHAND_END_RE = re.compile(r"\s\+(\d+(?:\.\d+)?)\s*(k|m|b)\s*[.!?]?\s*$", re.I)
VERBOSE_RE = re.compile(r"\b(?:use|spend)\s+(\d+(?:\.\d+)?)\s*(k|m|b)\s*tokens?\b", re.I)

MULTIPLIERS = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}


def _parse_budget_match(value: str, suffix: str) -> int:
    return int(float(value) * MULTIPLIERS[suffix.lower()])


def parseTokenBudget(text: str, *_args: Any, **_kwargs: Any) -> int | None:
    """Parse shorthand or verbose token budget syntax."""

    for pattern in (SHORTHAND_START_RE, SHORTHAND_END_RE, VERBOSE_RE):
        match = pattern.search(text or "")
        if match:
            return _parse_budget_match(match.group(1), match.group(2))
    return None


def findTokenBudgetPositions(text: str, *_args: Any, **_kwargs: Any) -> list[dict[str, int]]:
    """Return character spans for all token budget mentions."""

    value = text or ""
    positions: list[dict[str, int]] = []
    start_match = SHORTHAND_START_RE.search(value)
    if start_match:
        raw = start_match.group(0)
        offset = start_match.start() + len(raw) - len(raw.lstrip())
        positions.append({"start": offset, "end": start_match.end()})

    end_match = SHORTHAND_END_RE.search(value)
    if end_match:
        end_start = end_match.start() + 1
        already_covered = any(pos["start"] <= end_start < pos["end"] for pos in positions)
        if not already_covered:
            positions.append({"start": end_start, "end": end_match.end()})

    for match in VERBOSE_RE.finditer(value):
        positions.append({"start": match.start(), "end": match.end()})
    return positions


def getBudgetContinuationMessage(pct: int, turnTokens: int, budget: int, *_args: Any, **_kwargs: Any) -> str:
    """Return the continuation nudge used when a budget target is not met."""

    return (
        f"Stopped at {pct}% of token target ({turnTokens:,} / {budget:,}). "
        "Keep working - do not summarize."
    )


__all__ = ["findTokenBudgetPositions", "getBudgetContinuationMessage", "parseTokenBudget"]
