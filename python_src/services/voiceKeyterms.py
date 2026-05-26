"""Voice keyword helpers."""

from __future__ import annotations

import re
from typing import Any


async def splitIdentifier(identifier: str) -> list[str]:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", str(identifier or ""))
    value = re.sub(r"[_\-./\\]+", " ", value)
    return [part.lower() for part in value.split() if part]


async def getVoiceKeyterms(items: list[Any] | None = None) -> list[str]:
    """Extract pronounceable key terms from identifiers, paths, and messages."""

    terms: list[str] = []
    for item in items or []:
        if isinstance(item, dict):
            candidates = [item.get("name"), item.get("path"), item.get("title"), item.get("content")]
        else:
            candidates = [item]
        for candidate in candidates:
            if not candidate:
                continue
            for term in await splitIdentifier(str(candidate)):
                if len(term) > 1 and term not in terms:
                    terms.append(term)
    return terms
