"""Slash command implementation for remote-control bridge sessions."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from python_src.bridge.bridgeEnabled import getBridgeDisabledReason, isBridgeEnabled
from python_src.bridge.bridgeMain import runBridgeHeadless

DoneCallback = Callable[[Any], Any | Awaitable[Any]]


async def _notify(onDone: DoneCallback | None, payload: Any) -> None:
    if onDone is None:
        return
    result = onDone(payload)
    if hasattr(result, "__await__"):
        await result


async def call(
    onDone: DoneCallback | None = None,
    context: dict[str, Any] | None = None,
    args: str | None = None,
) -> dict[str, Any]:
    """Connect the current process to a local remote-control bridge.

    The production TypeScript command opens a remote-control session. The
    migration keeps that contract but defaults to the in-memory bridge
    transport, which makes the command safe for tests and local DeepSeek-backed
    development.
    """

    if not isBridgeEnabled():
        result = {"ok": False, "enabled": False, "message": await getBridgeDisabledReason()}
        await _notify(onDone, result["message"])
        return result

    session_id = (args or "").strip() or None
    app_state = context.get("appState", {}) if isinstance(context, dict) else {}
    options = {
        "sessionId": session_id,
        "quiet": True,
        "envless": False,
        "sdkUrl": app_state.get("bridgeSdkUrl") or "memory://bridge",
    }
    handle = await runBridgeHeadless(options)
    result = {
        "ok": True,
        "enabled": True,
        "mode": handle.get("mode"),
        "sessionId": handle.get("sessionId"),
    }
    await _notify(onDone, f"Remote control bridge ready: {result['sessionId']}")
    return result
