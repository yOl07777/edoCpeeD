from __future__ import annotations

import asyncio
from typing import Awaitable, TypeVar


T = TypeVar("T")


async def sleep(ms: int | float, signal: object | None = None, opts: dict | None = None) -> None:
    if getattr(signal, "aborted", False):
        if opts and (opts.get("throwOnAbort") or opts.get("abortError")):
            raise (opts.get("abortError")() if opts.get("abortError") else RuntimeError("aborted"))
        return
    await asyncio.sleep(max(0, float(ms)) / 1000)
    if getattr(signal, "aborted", False) and opts and (opts.get("throwOnAbort") or opts.get("abortError")):
        raise (opts.get("abortError")() if opts.get("abortError") else RuntimeError("aborted"))


async def withTimeout(promise: Awaitable[T], ms: int | float, message: str) -> T:
    try:
        return await asyncio.wait_for(promise, timeout=max(0, float(ms)) / 1000)
    except asyncio.TimeoutError as exc:
        raise TimeoutError(message) from exc
