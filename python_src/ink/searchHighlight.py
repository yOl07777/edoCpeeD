from __future__ import annotations

from typing import Any


async def applySearchHighlight(*args: Any, **kwargs: Any) -> Any:
    text = str(args[0] if args else kwargs.get("text", ""))
    query = str(args[1] if len(args) > 1 else kwargs.get("query", ""))
    case_sensitive = bool(kwargs.get("caseSensitive", False))
    marker = str(kwargs.get("marker", "^"))
    haystack = text if case_sensitive else text.lower()
    needle = query if case_sensitive else query.lower()
    ranges: list[dict[str, int]] = []
    if needle:
        start = 0
        while True:
            index = haystack.find(needle, start)
            if index < 0:
                break
            ranges.append({"start": index, "end": index + len(query)})
            start = index + max(1, len(query))
    overlay = [" "] * len(text)
    for item in ranges:
        for index in range(item["start"], min(item["end"], len(overlay))):
            overlay[index] = marker
    return {"provider": "deepseek", "text": text, "query": query, "ranges": ranges, "overlay": "".join(overlay)}
