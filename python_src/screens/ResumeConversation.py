"""Resume-conversation screen shim."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


_PR_RE = re.compile(r"github\.com/[^/]+/[^/]+/pull/(\d+)")


def parsePrIdentifier(value: str | int | bool | None) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    text = str(value).strip()
    if text.isdigit() and int(text) > 0:
        return int(text)
    match = _PR_RE.search(text)
    return int(match.group(1)) if match else None


async def ResumeConversation(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Return a resume-selection model for migrated Python callers."""

    props: dict[str, Any] = {}
    if args and isinstance(args[0], dict):
        props.update(args[0])
    props.update(kwargs)

    worktrees = [str(Path(item)) for item in props.get("worktreePaths") or []]
    filter_by_pr = props.get("filterByPr")
    pr_number = parsePrIdentifier(filter_by_pr)
    return {
        "type": "resume_conversation",
        "commands": props.get("commands") or [],
        "worktreePaths": worktrees,
        "initialTools": props.get("initialTools") or [],
        "debug": bool(props.get("debug", False)),
        "forkSession": bool(props.get("forkSession", False)),
        "taskListId": props.get("taskListId"),
        "filterByPr": filter_by_pr,
        "prNumber": pr_number,
        "initialSearchQuery": props.get("initialSearchQuery"),
        "disableSlashCommands": bool(props.get("disableSlashCommands", False)),
        "provider": "deepseek",
    }


__all__ = ["ResumeConversation", "parsePrIdentifier"]
