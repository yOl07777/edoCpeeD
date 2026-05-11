from __future__ import annotations

from typing import Any


async def UltrareviewOverageDialog(size: int, max_chars: int) -> dict[str, Any]:
    return {
        "title": "Review diff is large",
        "size": size,
        "max_chars": max_chars,
        "message": f"Diff size {size} exceeds the configured review limit {max_chars}.",
    }
