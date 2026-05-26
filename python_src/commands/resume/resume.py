"""Local `/resume` command shim."""

from __future__ import annotations

from typing import Any, Iterable

from python_src.history import makeHistoryReader


async def filterResumableSessions(sessions: Iterable[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    if sessions is not None:
        return [s for s in sessions if s and not s.get("disabled") and (s.get("id") or s.get("sessionId") or s.get("display"))]
    result: list[dict[str, Any]] = []
    async for entry in makeHistoryReader():
        display = entry.get("display", "")
        result.append({"display": display, "pastedContents": entry.get("pastedContents", {})})
    return result


def formatResumableSessions(sessions: list[dict[str, Any]]) -> str:
    if not sessions:
        return "No resumable local sessions found."
    lines = ["Resumable local sessions:"]
    for idx, session in enumerate(sessions[:20], 1):
        label = str(session.get("display") or session.get("id") or session.get("sessionId") or "untitled")
        lines.append(f"{idx}. {label[:120]}")
    return "\n".join(lines)


async def call(onDone: Any = None, *_args: Any, **_kwargs: Any) -> dict[str, Any] | None:
    sessions = await filterResumableSessions()
    message = formatResumableSessions(sessions)
    if callable(onDone):
        try:
            onDone(message, {"display": "system"})
        except TypeError:
            onDone(message)
        return None
    return {"type": "text", "value": message, "sessions": sessions}
