from __future__ import annotations

from contextvars import ContextVar
from typing import Any, Callable, TypeVar


WORKLOAD_CRON = "cron"
_workload: ContextVar[str | None] = ContextVar("deepseek_workload", default=None)
T = TypeVar("T")


def getWorkload() -> str | None:
    return _workload.get()


def runWithWorkload(workload: str | None, fn: Callable[[], T]) -> T:
    token = _workload.set(workload)
    try:
        return fn()
    finally:
        _workload.reset(token)
