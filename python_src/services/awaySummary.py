"""Away summary generation for local sessions."""

from __future__ import annotations

from typing import Any


async def generateAwaySummary(events: list[dict[str, Any]] | list[str] | None = None, max_items: int = 5) -> dict[str, Any]:
    events = events or []
    lines: list[str] = []
    for event in events[-max_items:]:
        if isinstance(event, dict):
            text = event.get("summary") or event.get("message") or event.get("content") or event.get("event")
        else:
            text = event
        if text:
            lines.append(str(text))
    summary = "No activity while you were away." if not lines else "\n".join(f"- {line}" for line in lines)
    return {"summary": summary, "event_count": len(events), "shown_count": len(lines)}
