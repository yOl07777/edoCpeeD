"""Remote structured IO over the migrated transport shims."""

from __future__ import annotations

import asyncio
import os
from typing import AsyncIterable, Any

from .ndjsonSafeStringify import ndjsonSafeStringify
from .structuredIO import StructuredIO
from .transports.transportUtils import getTransportForUrl


class RemoteIO(StructuredIO):
    def __init__(
        self,
        streamUrl: str,
        initialPrompt: AsyncIterable[str] | list[str] | None = None,
        replayUserMessages: bool | None = None,
    ) -> None:
        self.buffer: list[str] = []
        super().__init__(self.buffer, replayUserMessages)
        headers: dict[str, str] = {}
        token = os.getenv("CLAUDE_CODE_SESSION_ACCESS_TOKEN") or os.getenv("DEEPSEEK_SESSION_ACCESS_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.transport = getTransportForUrl(streamUrl, headers, os.getenv("DEEPCODE_SESSION_ID"))
        self.transport.setOnData(self._on_data)
        self.transport.setOnClose(lambda: setattr(self, "inputClosed", True))
        self._connect_task = asyncio.create_task(self.transport.connect()) if _loop_running() else None
        if initialPrompt:
            self._load_initial_prompt(initialPrompt)

    def _load_initial_prompt(self, prompt: AsyncIterable[str] | list[str]) -> None:
        async def load() -> None:
            async for chunk in _aiter(prompt):
                self.buffer.append(str(chunk).rstrip("\n") + "\n")

        if _loop_running():
            asyncio.create_task(load())
        else:
            asyncio.run(load())

    def _on_data(self, data: str) -> None:
        self.buffer.append(data if data.endswith("\n") else data + "\n")

    async def write(self, message: dict[str, Any]) -> None:
        await self.transport.write(message)
        await super().write(message)
        if os.getenv("CLAUDE_CODE_ENVIRONMENT_KIND") == "bridge" and message.get("type") == "control_request":
            self.buffer.append(ndjsonSafeStringify(message) + "\n")

    def close(self) -> None:
        self.transport.close()
        self.inputClosed = True


def _loop_running() -> bool:
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


async def _aiter(value: AsyncIterable[str] | list[str]):
    if hasattr(value, "__aiter__"):
        async for item in value:  # type: ignore[union-attr]
            yield item
    else:
        for item in value:  # type: ignore[union-attr]
            yield item
