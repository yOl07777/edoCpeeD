from __future__ import annotations

import json
from collections import Counter
from typing import Any


async def generateToolUseSummary(tool_events: list[dict[str, Any]], *, max_items: int = 20) -> dict[str, Any]:
    names = []
    lines = []
    for event in tool_events[:max_items]:
        name = event.get("name") or event.get("tool") or event.get("function", {}).get("name") or "unknown"
        names.append(str(name))
        status = event.get("status") or event.get("exit_code") or event.get("result", {}).get("status") or "ok"
        args = event.get("arguments") or event.get("args") or {}
        arg_text = json.dumps(args, ensure_ascii=False) if isinstance(args, dict) else str(args)
        lines.append(f"- {name}: {status} {arg_text[:160]}")
    counts = Counter(names)
    return {
        "count": len(tool_events),
        "by_tool": dict(counts),
        "summary": "\n".join(lines),
        "truncated": len(tool_events) > max_items,
    }
