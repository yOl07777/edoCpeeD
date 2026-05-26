"""Coalescing uploader for worker state and external metadata patches."""

from __future__ import annotations

import asyncio
import random
from typing import Any, Awaitable, Callable


def coalescePatches(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in overlay.items():
        if (
            key in {"external_metadata", "internal_metadata"}
            and isinstance(merged.get(key), dict)
            and isinstance(value, dict)
        ):
            merged[key] = {**merged[key], **value}
        else:
            merged[key] = value
    return merged


class WorkerStateUploader:
    def __init__(self, config: dict[str, Any] | None = None, **kwargs: Any) -> None:
        self.config = {**(config or {}), **kwargs}
        self.send: Callable[[dict[str, Any]], Awaitable[bool] | bool] = self.config.get("send") or (lambda _body: True)
        self.baseDelayMs = int(self.config.get("baseDelayMs", 100))
        self.maxDelayMs = int(self.config.get("maxDelayMs", 5_000))
        self.jitterMs = int(self.config.get("jitterMs", 0))
        self.pending: dict[str, Any] | None = None
        self.closed = False
        self._task: asyncio.Task[None] | None = None

    def enqueue(self, patch: dict[str, Any]) -> None:
        if self.closed:
            return
        self.pending = coalescePatches(self.pending, patch) if self.pending else dict(patch)
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._drain())

    def close(self) -> None:
        self.closed = True
        self.pending = None

    async def flush(self) -> None:
        if self._task is not None:
            await self._task

    async def _drain(self) -> None:
        if self.closed or not self.pending:
            return
        payload = self.pending
        self.pending = None
        failures = 0
        while not self.closed:
            result = self.send(payload)
            ok = await result if asyncio.iscoroutine(result) or isinstance(result, asyncio.Future) else result
            if ok:
                if self.pending and not self.closed:
                    payload = self.pending
                    self.pending = None
                    failures = 0
                    continue
                return
            failures += 1
            await asyncio.sleep(self._retry_delay(failures) / 1000)
            if self.pending and not self.closed:
                payload = coalescePatches(payload, self.pending)
                self.pending = None

    def _retry_delay(self, failures: int) -> float:
        return min(self.baseDelayMs * (2 ** max(0, failures - 1)), self.maxDelayMs) + random.random() * self.jitterMs
