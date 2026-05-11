from __future__ import annotations

import asyncio
import itertools
import time
from dataclasses import dataclass

from deepseek_code.config import DeepSeekConfig


@dataclass(frozen=True)
class DeepSeekTarget:
    api_key: str
    endpoint: str
    model: str

    @property
    def chat_url(self) -> str:
        return f"{self.endpoint.rstrip('/')}/chat/completions"


class DeepSeekLoadBalancer:
    def __init__(self, config: DeepSeekConfig):
        if not config.api_keys:
            raise ValueError("DEEPSEEK_API_KEYS is empty. Set at least one DeepSeek API key.")
        targets = [
            DeepSeekTarget(api_key=key, endpoint=endpoint, model=model)
            for key, endpoint, model in itertools.product(
                config.api_keys,
                config.endpoints,
                config.models,
            )
        ]
        self._targets = targets
        self._cooldowns: dict[DeepSeekTarget, float] = {}
        self._index = 0
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(config.max_concurrency)
        self._cooldown_seconds = config.cooldown_seconds

    @property
    def semaphore(self) -> asyncio.Semaphore:
        return self._semaphore

    async def next_target(self, *, preferred_model: str | None = None) -> DeepSeekTarget:
        async with self._lock:
            now = time.monotonic()
            candidates = [
                target
                for target in self._targets
                if self._cooldowns.get(target, 0.0) <= now
                and (preferred_model is None or target.model == preferred_model)
            ]
            if not candidates and preferred_model is not None:
                candidates = [
                    target
                    for target in self._targets
                    if self._cooldowns.get(target, 0.0) <= now
                ]
            if not candidates:
                raise RuntimeError("No DeepSeek target is currently available; all are cooling down.")
            target = candidates[self._index % len(candidates)]
            self._index += 1
            return target

    def mark_failure(self, target: DeepSeekTarget, status_code: int | None) -> None:
        if status_code in {401, 429} or (status_code is not None and status_code >= 500):
            self._cooldowns[target] = time.monotonic() + self._cooldown_seconds

    def mark_success(self, target: DeepSeekTarget) -> None:
        self._cooldowns.pop(target, None)
