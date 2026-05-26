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
        errors: list[str] = []
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
                    last_error = DeepSeekAPIError(
                        self._format_response_error("request", target, response.status_code, response.text),
                        status_code=response.status_code,
                    )
                    errors.append(str(last_error))
                    await self._backoff(attempt)
                    continue
                self.load_balancer.mark_success(target)
                return response.json()
            except (httpx.HTTPError, asyncio.TimeoutError) as exc:
                self.load_balancer.mark_failure(target, None)
                last_error = DeepSeekAPIError(self._format_exception("request", target, exc))
                errors.append(str(last_error))
                await self._backoff(attempt)
        raise DeepSeekAPIError(self._format_retry_failure("request", last_error, errors)) from last_error

    async def stream(self, request: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
        request = {**request, "stream": True}
        last_error: Exception | None = None
        errors: list[str] = []
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
                                self._format_response_error(
                                    "stream",
                                    target,
                                    response.status_code,
                                    body.decode("utf-8", errors="replace"),
                                ),
                                status_code=response.status_code,
                            )
                            errors.append(str(last_error))
                            await self._backoff(attempt)
                            continue
                        async for event in self._iter_sse(response):
                            yield event
                self.load_balancer.mark_success(target)
                return
            except (httpx.HTTPError, asyncio.TimeoutError) as exc:
                self.load_balancer.mark_failure(target, None)
                last_error = DeepSeekAPIError(self._format_exception("stream", target, exc))
                errors.append(str(last_error))
                await self._backoff(attempt)
        raise DeepSeekAPIError(self._format_retry_failure("stream", last_error, errors)) from last_error

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
    def _format_response_error(kind: str, target: DeepSeekTarget, status_code: int, body: str) -> str:
        body = (body or "").strip()
        if len(body) > 800:
            body = body[:800] + "... [truncated]"
        suffix = f": {body}" if body else ""
        return f"{kind} HTTP {status_code} from {target.chat_url}{suffix}"

    @staticmethod
    def _format_exception(kind: str, target: DeepSeekTarget, exc: Exception) -> str:
        detail = str(exc).strip() or exc.__class__.__name__
        return f"{kind} {exc.__class__.__name__} from {target.chat_url}: {detail}"

    @staticmethod
    def _format_retry_failure(kind: str, last_error: Exception | None, errors: list[str]) -> str:
        if not errors:
            return f"DeepSeek {kind} failed after retries: {last_error}"
        unique_errors = list(dict.fromkeys(errors))
        attempts = "; ".join(unique_errors[-3:])
        return f"DeepSeek {kind} failed after retries: {last_error}. Attempts: {attempts}"

    @staticmethod
    async def _backoff(attempt: int) -> None:
        await asyncio.sleep(min(2.0, 0.25 * (2**attempt)))
