"""Compact warning suppression hook shim."""

from __future__ import annotations

from typing import Any

from .compactWarningState import compactWarningStore


async def useCompactWarningSuppression(*_: Any, **__: Any) -> bool:
    return bool(compactWarningStore.get("suppressed", False))


__all__ = ["useCompactWarningSuppression"]
