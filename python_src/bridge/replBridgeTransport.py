"""Transport adapters used by the Python REPL bridge migration."""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable
from urllib.parse import urljoin

from python_src.cli.transports.SSETransport import SSETransport
from python_src.cli.transports.WebSocketTransport import WebSocketTransport


Callback = Callable[..., Any]


async def _maybe_await(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


@dataclass
class ReplBridgeTransport:
    """Common transport surface for v1 hybrid and v2 CCR/SSE paths."""

    read_transport: Any
    writer: Any | None = None
    epoch: int | None = None
    droppedBatchCount: int = 0
    closed: bool = False
    connected: bool = False
    sent: list[Any] = field(default_factory=list)
    state_reports: list[Any] = field(default_factory=list)
    metadata_reports: list[dict[str, Any]] = field(default_factory=list)
    delivery_reports: list[tuple[str, str]] = field(default_factory=list)
    _on_connect: Callback | None = None

    async def write(self, message: Any) -> None:
        if self.closed:
            return
        self.sent.append(message)
        target = self.writer or self.read_transport
        write_event = getattr(target, "writeEvent", None)
        write = getattr(target, "write", None)
        if write_event:
            await _maybe_await(write_event(message))
        elif write:
            await _maybe_await(write(message))

    async def writeBatch(self, messages: list[Any]) -> None:
        for message in messages:
            if self.closed:
                break
            await self.write(message)

    def close(self) -> None:
        self.closed = True
        self.connected = False
        close = getattr(self.writer, "close", None)
        if close:
            close()
        close = getattr(self.read_transport, "close", None)
        if close:
            close()

    def isConnectedStatus(self) -> bool:
        checker = getattr(self.read_transport, "isConnectedStatus", None)
        if checker:
            return bool(checker())
        return self.connected or bool(getattr(self.read_transport, "connected", False))

    def getStateLabel(self) -> str:
        if self.closed:
            return "closed"
        if self.isConnectedStatus():
            return "connected"
        return "connecting"

    def setOnData(self, callback: Callback) -> None:
        setter = getattr(self.read_transport, "setOnData", None)
        if setter:
            setter(callback)

    def setOnClose(self, callback: Callback) -> None:
        setter = getattr(self.read_transport, "setOnClose", None)
        if setter:
            setter(callback)

    def setOnConnect(self, callback: Callback) -> None:
        self._on_connect = callback

    def connect(self) -> None:
        self.connected = True
        connect = getattr(self.read_transport, "connect", None)
        if connect:
            result = connect()
            if inspect.isawaitable(result):
                result.close()
        if self._on_connect:
            self._on_connect()

    def getLastSequenceNum(self) -> int:
        getter = getattr(self.read_transport, "getLastSequenceNum", None)
        if getter:
            try:
                return int(getter())
            except (TypeError, ValueError):
                return 0
        return int(getattr(self.read_transport, "lastSequenceNum", 0) or 0)

    def reportState(self, state: Any) -> None:
        self.state_reports.append(state)
        reporter = getattr(self.writer, "reportState", None)
        if reporter:
            reporter(state)

    def reportMetadata(self, metadata: dict[str, Any]) -> None:
        self.metadata_reports.append(metadata)
        reporter = getattr(self.writer, "reportMetadata", None)
        if reporter:
            reporter(metadata)

    def reportDelivery(self, eventId: str, status: str) -> None:
        self.delivery_reports.append((eventId, status))
        reporter = getattr(self.writer, "reportDelivery", None)
        if reporter:
            reporter(eventId, status)

    async def flush(self) -> None:
        flusher = getattr(self.writer, "flush", None)
        if flusher:
            await _maybe_await(flusher())


def createV1ReplTransport(hybrid: Any) -> ReplBridgeTransport:
    dropped = int(getattr(hybrid, "droppedBatchCount", 0) or 0)
    return ReplBridgeTransport(read_transport=hybrid, writer=hybrid, droppedBatchCount=dropped)


async def createV2ReplTransport(opts: dict[str, Any] | None = None, **kwargs: Any) -> ReplBridgeTransport:
    options = {**(opts or {}), **kwargs}
    session_url = str(options.get("sessionUrl") or options.get("session_url") or "").rstrip("/")
    session_id = str(options.get("sessionId") or options.get("session_id") or "")
    epoch = options.get("epoch")
    stream_url = urljoin(session_url + "/", "worker/events/stream") if session_url else "memory://worker/events/stream"

    sse = SSETransport(stream_url, {}, session_id or None)
    sse.lastSequenceNum = int(options.get("initialSequenceNum") or 0)
    writer = options.get("writer")
    transport = ReplBridgeTransport(read_transport=sse, writer=writer or sse, epoch=epoch)
    if options.get("outboundOnly"):
        transport.connected = True
    return transport
