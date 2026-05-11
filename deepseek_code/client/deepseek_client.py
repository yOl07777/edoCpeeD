from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any

import httpx

from deepseek_code.client.base import BaseLLMClient
from deepseek_code.client.load_balancer import DeepSeekLoadBalancer, DeepSeekTarget
from deepseek_code.config import DeepSeekConfig


class DeepSeekAPIError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class DeepSeekClient(BaseLLMClient):
    def __init__(
        self,
        config: DeepSeekConfig,
        *,
        load_balancer: DeepSeekLoadBalancer | None = None,
        http_client: httpx.AsyncClient | None = None,
    ):
        self.config = config
        self.load_balancer = load_balancer or DeepSeekLoadBalancer(config)
        self._client = http_client or httpx.AsyncClient(timeout=config.timeout_seconds)
        self._owns_client = http_client is None

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> "DeepSeekClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def complete(self, request: dict[str, Any]) -> dict[str, Any]:
        request = {**request, "stream": False}
        last_error: Exception | None = None
        for attempt in range(self.config.max_retries):
            target = await self.load_balancer.next_target(preferred_model=request.get("model"))
            try:
                async with self.load_balancer.semaphore:
                    response = await self._client.post(
                        target.chat_url,
                        headers=self._headers(target),
                        json={**request, "model": request.get("model") or target.model},
                    )
                if response.status_code >= 400:
                    self.load_balancer.mark_failure(target, response.status_code)
                    last_error = DeepSeekAPIError(response.text, status_code=response.status_code)
                    await self._backoff(attempt)
                    continue
                self.load_balancer.mark_success(target)
                return response.json()
            except (httpx.HTTPError, asyncio.TimeoutError) as exc:
                self.load_balancer.mark_failure(target, None)
                last_error = exc
                await self._backoff(attempt)
        raise DeepSeekAPIError(f"DeepSeek request failed after retries: {last_error}") from last_error

    async def stream(self, request: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
        request = {**request, "stream": True}
        last_error: Exception | None = None
        for attempt in range(self.config.max_retries):
            target = await self.load_balancer.next_target(preferred_model=request.get("model"))
            try:
                async with self.load_balancer.semaphore:
                    async with self._client.stream(
                        "POST",
                        target.chat_url,
                        headers=self._headers(target),
                        json={**request, "model": request.get("model") or target.model},
                    ) as response:
                        if response.status_code >= 400:
                            body = await response.aread()
                            self.load_balancer.mark_failure(target, response.status_code)
                            last_error = DeepSeekAPIError(
                                body.decode("utf-8", errors="replace"),
                                status_code=response.status_code,
                            )
                            await self._backoff(attempt)
                            continue
                        async for event in self._iter_sse(response):
                            yield event
                self.load_balancer.mark_success(target)
                return
            except (httpx.HTTPError, asyncio.TimeoutError) as exc:
                self.load_balancer.mark_failure(target, None)
                last_error = exc
                await self._backoff(attempt)
        raise DeepSeekAPIError(f"DeepSeek stream failed after retries: {last_error}") from last_error

    @staticmethod
    def _headers(target: DeepSeekTarget) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {target.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream, application/json",
        }

    @staticmethod
    async def _iter_sse(response: httpx.Response) -> AsyncIterator[dict[str, Any]]:
        async for line in response.aiter_lines():
            line = line.strip()
            if not line or line.startswith(":"):
                continue
            if line.startswith("data:"):
                data = line[5:].strip()
                if data == "[DONE]":
                    return
                yield json.loads(data)

    @staticmethod
    async def _backoff(attempt: int) -> None:
        await asyncio.sleep(min(2.0, 0.25 * (2**attempt)))
