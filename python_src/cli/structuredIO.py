"""Structured stdin/stdout protocol helpers for SDK/headless mode."""

from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import AsyncIterable
from typing import Any, Callable

from .ndjsonSafeStringify import ndjsonSafeStringify

SANDBOX_NETWORK_ACCESS_TOOL_NAME = "SandboxNetworkAccess"


class StructuredIO:
    def __init__(self, input: AsyncIterable[str] | list[str] | None = None, replayUserMessages: bool | None = None) -> None:
        self.input = input or []
        self.replayUserMessages = bool(replayUserMessages)
        self.pendingRequests: dict[str, asyncio.Future[Any]] = {}
        self.outbound: list[dict[str, Any]] = []
        self.prependedLines: list[str] = []
        self.inputClosed = False
        self.unexpectedResponseCallback: Callable[[dict[str, Any]], Any] | None = None
        self.resolvedToolUseIds: set[str] = set()
        self.restoredWorkerState = asyncio.Future()
        self.restoredWorkerState.set_result(None)

    @property
    def internalEventsPending(self) -> int:
        return 0

    async def flushInternalEvents(self) -> None:
        return None

    def prependUserMessage(self, content: str) -> None:
        self.prependedLines.append(
            ndjsonSafeStringify(
                {
                    "type": "user",
                    "session_id": "",
                    "message": {"role": "user", "content": content},
                    "parent_tool_use_id": None,
                }
            )
            + "\n"
        )

    def setUnexpectedResponseCallback(self, callback: Callable[[dict[str, Any]], Any]) -> None:
        self.unexpectedResponseCallback = callback

    async def read(self):
        while self.prependedLines:
            parsed = await self.processLine(self.prependedLines.pop(0).strip())
            if parsed is not None:
                yield parsed
        async for block in _aiter(self.input):
            for line in str(block).splitlines():
                parsed = await self.processLine(line)
                if parsed is not None:
                    yield parsed
                while self.prependedLines:
                    prepended = await self.processLine(self.prependedLines.pop(0).strip())
                    if prepended is not None:
                        yield prepended
        self.inputClosed = True

    @property
    def structuredInput(self):
        return self.read()

    async def processLine(self, line: str) -> dict[str, Any] | None:
        if not line.strip():
            return None
        try:
            message = json.loads(line)
        except ValueError:
            return None
        if not isinstance(message, dict):
            return None
        if message.get("type") == "control_response":
            await self._handleControlResponse(message)
            return None
        if message.get("type") == "update_environment_variables" and isinstance(message.get("variables"), dict):
            import os

            for key, value in message["variables"].items():
                if value is None:
                    os.environ.pop(str(key), None)
                else:
                    os.environ[str(key)] = str(value)
            return None
        return message

    async def _handleControlResponse(self, response: dict[str, Any]) -> None:
        body = response.get("response") if isinstance(response.get("response"), dict) else {}
        request_id = body.get("request_id")
        future = self.pendingRequests.pop(str(request_id), None)
        if future is None:
            if self.unexpectedResponseCallback:
                result = self.unexpectedResponseCallback(response)
                if asyncio.iscoroutine(result):
                    await result
            return
        if body.get("subtype") == "error":
            future.set_exception(RuntimeError(str(body.get("error") or "control request failed")))
        else:
            future.set_result(body.get("response", body))

    async def write(self, message: dict[str, Any]) -> None:
        self.outbound.append(message)

    async def sendRequest(self, request: dict[str, Any], timeout: float | None = None) -> Any:
        request_id = request.get("request_id") or str(uuid.uuid4())
        request["request_id"] = request_id
        future: asyncio.Future[Any] = asyncio.Future()
        self.pendingRequests[str(request_id)] = future
        await self.write({"type": "control_request", **request})
        return await asyncio.wait_for(future, timeout) if timeout else await future


async def _aiter(value: AsyncIterable[str] | list[str]):
    if hasattr(value, "__aiter__"):
        async for item in value:  # type: ignore[union-attr]
            yield item
    else:
        for item in value:  # type: ignore[union-attr]
            yield item
