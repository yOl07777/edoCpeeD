"""Serial ordered event uploader with batching, retry, and backpressure."""

from __future__ import annotations

import asyncio
import json
import random
from typing import Any, Awaitable, Callable, Generic, TypeVar

T = TypeVar("T")


class RetryableError(Exception):
    def __init__(self, message: str, retryAfterMs: int | float | None = None) -> None:
        super().__init__(message)
        self.retryAfterMs = retryAfterMs


class SerialBatchEventUploader(Generic[T]):
    def __init__(self, config: dict[str, Any] | None = None, **kwargs: Any) -> None:
        self.config = {**(config or {}), **kwargs}
        self.maxBatchSize = int(self.config.get("maxBatchSize", 100))
        self.maxBatchBytes = self.config.get("maxBatchBytes")
        self.maxQueueSize = int(self.config.get("maxQueueSize", 10_000))
        self.baseDelayMs = int(self.config.get("baseDelayMs", 100))
        self.maxDelayMs = int(self.config.get("maxDelayMs", 5_000))
        self.jitterMs = int(self.config.get("jitterMs", 0))
        self.maxConsecutiveFailures = self.config.get("maxConsecutiveFailures")
        self.send: Callable[[list[T]], Awaitable[None] | None] = self.config.get("send") or (lambda _batch: None)
        self.onBatchDropped = self.config.get("onBatchDropped")
        self._pending: list[T] = []
        self._closed = False
        self._draining = False
        self._dropped_batches = 0
        self._pending_at_close = 0
        self._flush_waiters: list[asyncio.Future[None]] = []
        self._space_available = asyncio.Event()
        self._space_available.set()

    @property
    def droppedBatchCount(self) -> int:
        return self._dropped_batches

    @property
    def pendingCount(self) -> int:
        return self._pending_at_close if self._closed else len(self._pending)

    async def enqueue(self, events: T | list[T]) -> None:
        if self._closed:
            return
        items = events if isinstance(events, list) else [events]
        if not items:
            return
        while len(self._pending) + len(items) > self.maxQueueSize and not self._closed:
            self._space_available.clear()
            await self._space_available.wait()
        if self._closed:
            return
        self._pending.extend(items)
        asyncio.create_task(self._drain())

    async def flush(self) -> None:
        if not self._pending and not self._draining:
            return
        asyncio.create_task(self._drain())
        future: asyncio.Future[None] = asyncio.get_running_loop().create_future()
        self._flush_waiters.append(future)
        await future

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._pending_at_close = len(self._pending)
        self._pending.clear()
        self._space_available.set()
        for waiter in self._flush_waiters:
            if not waiter.done():
                waiter.set_result(None)
        self._flush_waiters.clear()

    async def _drain(self) -> None:
        if self._draining or self._closed:
            return
        self._draining = True
        failures = 0
        try:
            while self._pending and not self._closed:
                batch = self._take_batch()
                if not batch:
                    continue
                try:
                    result = self.send(batch)
                    if asyncio.iscoroutine(result) or isinstance(result, asyncio.Future):
                        await result
                    failures = 0
                    self._space_available.set()
                except Exception as exc:
                    failures += 1
                    if self.maxConsecutiveFailures is not None and failures >= int(self.maxConsecutiveFailures):
                        self._dropped_batches += 1
                        if self.onBatchDropped:
                            self.onBatchDropped(len(batch), failures)
                        failures = 0
                        self._space_available.set()
                        continue
                    self._pending = batch + self._pending
                    retry_after = exc.retryAfterMs if isinstance(exc, RetryableError) else None
                    await asyncio.sleep(self._retry_delay(failures, retry_after) / 1000)
        finally:
            self._draining = False
            if not self._pending:
                for waiter in self._flush_waiters:
                    if not waiter.done():
                        waiter.set_result(None)
                self._flush_waiters.clear()

    def _take_batch(self) -> list[T]:
        if self.maxBatchBytes is None:
            batch = self._pending[: self.maxBatchSize]
            del self._pending[: len(batch)]
            return batch
        total = 0
        count = 0
        while count < len(self._pending) and count < self.maxBatchSize:
            try:
                item_bytes = len(json.dumps(self._pending[count], ensure_ascii=False, default=str).encode("utf-8"))
            except Exception:
                del self._pending[count]
                continue
            if count > 0 and total + item_bytes > int(self.maxBatchBytes):
                break
            total += item_bytes
            count += 1
        batch = self._pending[:count]
        del self._pending[:count]
        return batch

    def _retry_delay(self, failures: int, retry_after_ms: int | float | None = None) -> float:
        jitter = random.random() * self.jitterMs
        if retry_after_ms is not None:
            return max(self.baseDelayMs, min(float(retry_after_ms), self.maxDelayMs)) + jitter
        return min(self.baseDelayMs * (2 ** max(0, failures - 1)), self.maxDelayMs) + jitter
