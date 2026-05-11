from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


PERMISSION_LOG: list[dict[str, Any]] = []


def logPermissionDecision(context: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool_name": context.get("tool_name") or context.get("tool"),
        "decision": decision,
        "context": context,
    }
    PERMISSION_LOG.append(entry)
    return entry


def getPermissionLog() -> list[dict[str, Any]]:
    return list(PERMISSION_LOG)


def clearPermissionLog() -> None:
    PERMISSION_LOG.clear()
