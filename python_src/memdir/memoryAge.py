"""Memory freshness helpers.

The original TypeScript helpers are pure date math.  The Python migration keeps
the same public async shape used by generated shims while avoiding any model or
Anthropic dependency.
"""

from __future__ import annotations

import time
from typing import Any

MS_PER_DAY = 86_400_000


def _mtime_ms(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return time.time() * 1000


async def memoryAgeDays(mtimeMs: Any, *_args: Any, **_kwargs: Any) -> int:
    """Return floor-rounded elapsed days since an mtime in milliseconds."""

    elapsed = (time.time() * 1000 - _mtime_ms(mtimeMs)) / MS_PER_DAY
    return max(0, int(elapsed))


async def memoryAge(mtimeMs: Any, *_args: Any, **_kwargs: Any) -> str:
    """Return a compact human-readable memory age."""

    days = await memoryAgeDays(mtimeMs)
    if days == 0:
        return "today"
    if days == 1:
        return "yesterday"
    return f"{days} days ago"


async def memoryFreshnessText(mtimeMs: Any, *_args: Any, **_kwargs: Any) -> str:
    """Return a staleness caveat for memories older than yesterday."""

    days = await memoryAgeDays(mtimeMs)
    if days <= 1:
        return ""
    return (
        f"This memory is {days} days old. "
        "Memories are point-in-time observations, not live state; "
        "claims about code behavior or file:line citations may be outdated. "
        "Verify against current code before asserting as fact."
    )


async def memoryFreshnessNote(mtimeMs: Any, *_args: Any, **_kwargs: Any) -> str:
    """Return the staleness caveat wrapped for system-reminder consumers."""

    text = await memoryFreshnessText(mtimeMs)
    if not text:
        return ""
    return f"<system-reminder>{text}</system-reminder>\n"


__all__ = [
    "memoryAge",
    "memoryAgeDays",
    "memoryFreshnessNote",
    "memoryFreshnessText",
]
