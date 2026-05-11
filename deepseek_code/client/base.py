from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any


class BaseLLMClient(ABC):
    @abstractmethod
    async def complete(self, request: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def stream(self, request: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
        raise NotImplementedError
