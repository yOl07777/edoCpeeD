"""Ant-only bridge fault injection command."""

from __future__ import annotations

import os
from typing import Any

from python_src.bridge.bridgeDebug import BridgeFault, getBridgeDebugHandle, injectBridgeFault


USAGE = """/bridge-kick <subcommand>
  close <code>              fire ws_closed with the given code
  poll <status> [type]      next poll throws BridgeFatalError(status, type)
  poll transient            next poll throws a transient 503-style error
  register fail [N]         next N registers transient-fail
  register fatal            next register 403s
  reconnect-session fail    next POST /bridge/reconnect fails
  heartbeat <status>        next heartbeat throws BridgeFatalError(status)
  reconnect                 call reconnectEnvironmentWithSession directly
  status                    print bridge state"""


def _text(value: str) -> dict[str, str]:
    return {"type": "text", "value": value}


def _call_handle(handle: Any, method: str, *args: Any) -> bool:
    func = getattr(handle, method, None)
    if callable(func):
        func(*args)
        return True
    return False


async def call(args: str = "", *_unused: Any, **_kwargs: Any) -> dict[str, str]:
    handle = getBridgeDebugHandle()
    parts = (args or "").strip().split()
    sub = parts[0] if parts else ""
    a = parts[1] if len(parts) > 1 else ""
    b = parts[2] if len(parts) > 2 else ""

    if not sub:
        return _text(USAGE)

    if sub == "status":
        if handle and callable(getattr(handle, "describe", None)):
            return _text(str(handle.describe()))
        return _text("No bridge debug handle registered. Remote Control must be connected (USER_TYPE=ant).")

    if sub == "close":
        try:
            code = int(a)
        except ValueError:
            return _text(f"close: need a numeric code\n{USAGE}")
        if handle and _call_handle(handle, "fireClose", code):
            return _text(f"Fired transport close({code}). Watch debug.log for bridge recovery.")
        return _text("No bridge debug handle registered. Cannot fire a transport close.")

    if sub == "poll":
        if a == "transient":
            injectBridgeFault(BridgeFault(method="pollForWork", kind="transient", status=503, count=1))
            if handle:
                _call_handle(handle, "wakePollLoop")
            return _text("Next poll will throw a transient 503-style error.")
        try:
            status = int(a)
        except ValueError:
            return _text(f"poll: need 'transient' or a status code\n{USAGE}")
        error_type = b or ("not_found_error" if status == 404 else "authentication_error")
        injectBridgeFault(BridgeFault(method="pollForWork", kind="fatal", status=status, errorType=error_type, count=1))
        if handle:
            _call_handle(handle, "wakePollLoop")
        return _text(f"Next poll will throw BridgeFatalError({status}, {error_type}).")

    if sub == "register":
        if a == "fatal":
            injectBridgeFault(
                BridgeFault(
                    method="registerBridgeEnvironment",
                    kind="fatal",
                    status=403,
                    errorType="permission_error",
                    count=1,
                )
            )
            return _text("Next registerBridgeEnvironment will 403. Trigger with close/reconnect.")
        try:
            count = int(b) if b else 1
        except ValueError:
            count = 1
        injectBridgeFault(
            BridgeFault(method="registerBridgeEnvironment", kind="transient", status=503, count=max(1, count))
        )
        return _text(f"Next {max(1, count)} registerBridgeEnvironment call(s) will transient-fail.")

    if sub == "reconnect-session" and a == "fail":
        injectBridgeFault(
            BridgeFault(method="reconnectSession", kind="fatal", status=404, errorType="not_found_error", count=2)
        )
        return _text("Next 2 POST /bridge/reconnect calls will 404.")

    if sub == "heartbeat":
        try:
            status = int(a)
        except ValueError:
            status = 401
        injectBridgeFault(
            BridgeFault(
                method="heartbeatWork",
                kind="fatal",
                status=status,
                errorType="authentication_error" if status == 401 else "not_found_error",
                count=1,
            )
        )
        return _text(f"Next heartbeat will throw BridgeFatalError({status}).")

    if sub == "reconnect":
        if handle and _call_handle(handle, "forceReconnect"):
            return _text("Called reconnectEnvironmentWithSession(). Watch debug.log.")
        return _text("No bridge debug handle registered. Cannot force reconnect.")

    return _text(USAGE)


bridgeKick = {
    "type": "local",
    "name": "bridge-kick",
    "description": "Inject bridge failure states for manual recovery testing",
    "isEnabled": lambda: os.getenv("USER_TYPE") == "ant",
    "supportsNonInteractive": False,
    "call": call,
}

default = bridgeKick
