"""JWT decoding and token refresh scheduling helpers."""

from __future__ import annotations

import asyncio
import base64
import json
import time
from collections.abc import Awaitable, Callable
from typing import Any

TOKEN_REFRESH_BUFFER_MS = 5 * 60 * 1000
FALLBACK_REFRESH_INTERVAL_MS = 30 * 60 * 1000
MAX_REFRESH_FAILURES = 3
REFRESH_RETRY_DELAY_MS = 60_000


def _b64url_decode(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def decodeJwtPayload(token: str) -> dict[str, Any] | None:
    jwt = token.removeprefix("sk-ant-si-")
    parts = jwt.split(".")
    if len(parts) < 2:
        return None
    try:
        payload = json.loads(_b64url_decode(parts[1]).decode("utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def decodeJwtExpiry(token: str) -> int | None:
    payload = decodeJwtPayload(token)
    exp = payload.get("exp") if payload else None
    return int(exp) if isinstance(exp, (int, float)) else None


class TokenRefreshScheduler:
    def __init__(
        self,
        refresh: Callable[[str], Awaitable[dict[str, Any] | None]],
        on_token: Callable[[str, str], None] | None = None,
        refresh_buffer_ms: int = TOKEN_REFRESH_BUFFER_MS,
    ) -> None:
        self.refresh = refresh
        self.on_token = on_token
        self.refresh_buffer_ms = refresh_buffer_ms
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._failures: dict[str, int] = {}

    def schedule(self, sessionId: str, token: str) -> None:
        expiry = decodeJwtExpiry(token)
        if expiry:
            delay = max(expiry - time.time() - self.refresh_buffer_ms / 1000, 30)
        else:
            delay = FALLBACK_REFRESH_INTERVAL_MS / 1000
        self._replace(sessionId, delay)

    def scheduleFromExpiresIn(self, sessionId: str, expiresInSeconds: int) -> None:
        delay = max(expiresInSeconds - self.refresh_buffer_ms / 1000, 30)
        self._replace(sessionId, delay)

    def _replace(self, sessionId: str, delay: float) -> None:
        self.cancel(sessionId)
        self._tasks[sessionId] = asyncio.create_task(self._run(sessionId, delay))

    async def _run(self, sessionId: str, delay: float) -> None:
        try:
            await asyncio.sleep(delay)
            result = await self.refresh(sessionId)
            if not result:
                raise RuntimeError("refresh returned no token")
            token = result.get("token") or result.get("session_ingress_token")
            if isinstance(token, str):
                self._failures.pop(sessionId, None)
                if self.on_token:
                    self.on_token(sessionId, token)
                expires_in = result.get("expires_in")
                if isinstance(expires_in, (int, float)):
                    self.scheduleFromExpiresIn(sessionId, int(expires_in))
                else:
                    self.schedule(sessionId, token)
        except asyncio.CancelledError:
            raise
        except Exception:
            failures = self._failures.get(sessionId, 0) + 1
            self._failures[sessionId] = failures
            if failures <= MAX_REFRESH_FAILURES:
                self._replace(sessionId, REFRESH_RETRY_DELAY_MS / 1000)

    def cancel(self, sessionId: str) -> None:
        task = self._tasks.pop(sessionId, None)
        if task:
            task.cancel()

    def cancelAll(self) -> None:
        for sessionId in list(self._tasks):
            self.cancel(sessionId)


def createTokenRefreshScheduler(
    refresh: Callable[[str], Awaitable[dict[str, Any] | None]] | None = None,
    onToken: Callable[[str, str], None] | None = None,
    **kwargs: Any,
) -> TokenRefreshScheduler:
    refresh_fn = refresh or kwargs.get("refresh") or kwargs.get("refreshSessionToken")
    if refresh_fn is None:
        async def refresh_fn(_: str) -> dict[str, Any] | None:
            return None
    return TokenRefreshScheduler(
        refresh=refresh_fn,
        on_token=onToken or kwargs.get("onToken") or kwargs.get("on_token"),
        refresh_buffer_ms=int(kwargs.get("refreshBufferMs", TOKEN_REFRESH_BUFFER_MS)),
    )
