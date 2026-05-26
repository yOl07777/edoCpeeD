"""Bridge debug handle and fault injection helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BridgeFault:
    method: str
    kind: str
    status: int
    errorType: str | None = None
    count: int = 1


class InjectedBridgeFault(RuntimeError):
    def __init__(self, message: str, status: int, errorType: str | None = None, fatal: bool = False) -> None:
        super().__init__(message)
        self.status = status
        self.errorType = errorType
        self.fatal = fatal


_debug_handle: Any | None = None
_fault_queue: list[BridgeFault] = []


def registerBridgeDebugHandle(h: Any) -> None:
    global _debug_handle
    _debug_handle = h


def clearBridgeDebugHandle() -> None:
    global _debug_handle
    _debug_handle = None
    _fault_queue.clear()


def getBridgeDebugHandle() -> Any | None:
    return _debug_handle


def injectBridgeFault(fault: BridgeFault | dict[str, Any]) -> None:
    if isinstance(fault, dict):
        fault = BridgeFault(**fault)
    _fault_queue.append(fault)


def _consume(method: str) -> BridgeFault | None:
    for idx, fault in enumerate(_fault_queue):
        if fault.method == method:
            fault.count -= 1
            if fault.count <= 0:
                _fault_queue.pop(idx)
            return fault
    return None


def _throw_fault(fault: BridgeFault, context: str) -> None:
    raise InjectedBridgeFault(
        f"[injected {'fatal' if fault.kind == 'fatal' else 'transient'}] {context} {fault.status}",
        fault.status,
        fault.errorType,
        fatal=fault.kind == "fatal",
    )


def wrapApiForFaultInjection(api: Any) -> Any:
    class FaultInjectingApi:
        def __init__(self, wrapped: Any) -> None:
            self._wrapped = wrapped

        def __getattr__(self, name: str) -> Any:
            attr = getattr(self._wrapped, name)
            if name not in {"pollForWork", "registerBridgeEnvironment", "reconnectSession", "heartbeatWork"}:
                return attr

            async def call(*args: Any, **kwargs: Any) -> Any:
                fault = _consume(name)
                if fault:
                    _throw_fault(fault, name)
                return await attr(*args, **kwargs)

            return call

    return FaultInjectingApi(api)
