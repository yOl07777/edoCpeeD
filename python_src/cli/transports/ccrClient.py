"""Lightweight CCR v2 client used by the Python bridge transport shims."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from .SerialBatchEventUploader import SerialBatchEventUploader
from .WorkerStateUploader import WorkerStateUploader


class CCRInitError(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(f"CCRClient init failed: {reason}")
        self.reason = reason


def createStreamAccumulator() -> dict[str, Any]:
    return {"byMessage": {}, "scopeToMessage": {}}


def _scope_key(message: dict[str, Any]) -> str:
    return f"{message.get('session_id', '')}:{message.get('parent_tool_use_id') or ''}"


def accumulateStreamEvents(buffer: list[dict[str, Any]], state: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    touched: dict[int, dict[str, Any]] = {}
    by_message: dict[str, list[list[str]]] = state.setdefault("byMessage", {})
    scope_to_message: dict[str, str] = state.setdefault("scopeToMessage", {})

    for msg in buffer:
        event = msg.get("event") if isinstance(msg, dict) else None
        event_type = event.get("type") if isinstance(event, dict) else None
        if event_type == "message_start":
            message_id = event.get("message", {}).get("id")
            if isinstance(message_id, str):
                previous = scope_to_message.get(_scope_key(msg))
                if previous:
                    by_message.pop(previous, None)
                scope_to_message[_scope_key(msg)] = message_id
                by_message[message_id] = []
            out.append(msg)
        elif event_type == "content_block_delta" and event.get("delta", {}).get("type") == "text_delta":
            message_id = scope_to_message.get(_scope_key(msg))
            blocks = by_message.get(message_id or "")
            if blocks is None:
                out.append(msg)
                continue
            index = int(event.get("index") or 0)
            while len(blocks) <= index:
                blocks.append([])
            chunks = blocks[index]
            chunks.append(str(event.get("delta", {}).get("text", "")))
            key = id(chunks)
            if key in touched:
                touched[key]["event"]["delta"]["text"] = "".join(chunks)
                continue
            snapshot = {
                **msg,
                "event": {
                    "type": "content_block_delta",
                    "index": index,
                    "delta": {"type": "text_delta", "text": "".join(chunks)},
                },
            }
            touched[key] = snapshot
            out.append(snapshot)
        else:
            out.append(msg)
    return out


def clearStreamAccumulatorForMessage(state: dict[str, Any], assistant: dict[str, Any]) -> None:
    message_id = assistant.get("message", {}).get("id")
    if isinstance(message_id, str):
        state.setdefault("byMessage", {}).pop(message_id, None)
        scope = _scope_key(assistant)
        if state.setdefault("scopeToMessage", {}).get(scope) == message_id:
            state["scopeToMessage"].pop(scope, None)


@dataclass
class _Delivery:
    eventId: str
    status: str


class CCRClient:
    def __init__(self, transport: Any = None, sessionUrl: Any = "memory://session", opts: dict[str, Any] | None = None) -> None:
        self.transport = transport
        self.sessionUrl = str(sessionUrl)
        self.opts = opts or {}
        self.workerEpoch = 0
        self.closed = False
        self.initialized = False
        self.events: list[Any] = []
        self.internal_events: list[Any] = []
        self.deliveries: list[_Delivery] = []
        self.states: list[Any] = []
        self.metadata: list[dict[str, Any]] = []
        self.streamTextAccumulator = createStreamAccumulator()
        self.workerState = WorkerStateUploader({"send": self._send_state})
        self.eventUploader = SerialBatchEventUploader({"send": self._send_events, "maxBatchSize": 100, "maxQueueSize": 10_000})
        self.internalEventUploader = SerialBatchEventUploader({"send": self._send_internal_events, "maxBatchSize": 100, "maxQueueSize": 10_000})
        self.deliveryUploader = SerialBatchEventUploader({"send": self._send_deliveries, "maxBatchSize": 100, "maxQueueSize": 10_000})

    async def initialize(self, epoch: int | None = None) -> None:
        if self.closed:
            raise CCRInitError("closed")
        if epoch is None and self.opts.get("requireEpoch"):
            raise CCRInitError("missing_epoch")
        self.workerEpoch = int(epoch or self.opts.get("epoch") or 0)
        self.initialized = True

    async def writeEvent(self, message: dict[str, Any]) -> None:
        if message.get("type") == "assistant" and isinstance(message.get("message"), dict):
            clearStreamAccumulatorForMessage(self.streamTextAccumulator, message)
        await self.eventUploader.enqueue({"payload": message})

    async def writeInternalEvent(self, event: dict[str, Any]) -> None:
        await self.internalEventUploader.enqueue({"payload": event})

    def reportState(self, state: Any) -> None:
        self.states.append(state)
        self.workerState.enqueue({"worker_status": state})

    def reportMetadata(self, metadata: dict[str, Any]) -> None:
        self.metadata.append(metadata)
        self.workerState.enqueue({"external_metadata": metadata})

    def reportDelivery(self, eventId: str, status: str) -> None:
        self.deliveries.append(_Delivery(eventId, status))
        asyncio.create_task(self.deliveryUploader.enqueue({"eventId": eventId, "status": status}))

    async def flush(self) -> None:
        await self.eventUploader.flush()
        await self.internalEventUploader.flush()
        await self.deliveryUploader.flush()
        await self.workerState.flush()

    def close(self) -> None:
        self.closed = True
        self.eventUploader.close()
        self.internalEventUploader.close()
        self.deliveryUploader.close()
        self.workerState.close()

    def _send_events(self, batch: list[Any]) -> None:
        self.events.extend(batch)

    def _send_internal_events(self, batch: list[Any]) -> None:
        self.internal_events.extend(batch)

    def _send_deliveries(self, batch: list[Any]) -> None:
        return None

    def _send_state(self, body: dict[str, Any]) -> bool:
        return True
