from __future__ import annotations

from datetime import datetime
from typing import Any


def _timestamp(value: Any) -> float:
    if isinstance(value, datetime):
        return value.timestamp()
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        except ValueError:
            return 0.0
    return 0.0


def _get(log: Any, key: str) -> Any:
    return log.get(key) if isinstance(log, dict) else getattr(log, key, None)


def sortLogs(logs: list[Any]) -> list[Any]:
    """Sort log options newest-first by modified, then created."""

    return sorted(logs, key=lambda log: (_timestamp(_get(log, "modified")), _timestamp(_get(log, "created"))), reverse=True)


__all__ = ["sortLogs"]
