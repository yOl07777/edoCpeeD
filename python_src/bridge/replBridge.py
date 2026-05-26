"""REPL bridge core for the Python migration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from python_src.cli.transports.HybridTransport import HybridTransport

from .replBridgeHandle import setReplBridgeHandle
from .replBridgeTransport import ReplBridgeTransport, createV1ReplTransport, createV2ReplTransport


@dataclass
class ReplBridgeHandle:
    bridgeSessionId: str
    transport: ReplBridgeTransport
    accessToken: str | None = None
    sdkUrl: str | None = None
    messages: list[Any] = field(default_factory=list)
    closed: bool = False

    async def write(self, message: Any) -> None:
        self.messages.append(message)
        await self.transport.write(message)

    async def writeBatch(self, messages: list[Any]) -> None:
        self.messages.extend(messages)
        await self.transport.writeBatch(messages)

    def close(self) -> None:
        self.closed = True
        self.transport.close()

    async def stop(self) -> None:
        self.close()

    def updateAccessToken(self, token: str) -> None:
        self.accessToken = token


async def initBridgeCore(options: dict[str, Any] | None = None, **kwargs: Any) -> ReplBridgeHandle:
    opts = {**(options or {}), **kwargs}
    session_id = str(opts.get("sessionId") or opts.get("bridgeSessionId") or f"session_{uuid4().hex}")
    sdk_url = opts.get("sdkUrl") or opts.get("sessionUrl") or "memory://bridge"
    transport = opts.get("transport")
    if transport is None:
        if opts.get("useCcrV2") or opts.get("v2"):
            transport = await createV2ReplTransport(
                {
                    "sessionUrl": str(opts.get("sessionUrl") or sdk_url),
                    "ingressToken": str(opts.get("ingressToken") or opts.get("accessToken") or ""),
                    "sessionId": session_id,
                    "epoch": opts.get("epoch"),
                    "outboundOnly": opts.get("outboundOnly", False),
                }
            )
        else:
            transport = createV1ReplTransport(HybridTransport(str(sdk_url), {}, session_id))

    handle = ReplBridgeHandle(
        bridgeSessionId=session_id,
        transport=transport,
        accessToken=opts.get("accessToken"),
        sdkUrl=str(sdk_url),
    )
    setReplBridgeHandle(handle)
    return handle
