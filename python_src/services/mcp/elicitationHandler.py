"""MCP elicitation handler shim for Python runtime."""

from __future__ import annotations

import asyncio
from typing import Any, Callable

_elicitation_hooks: list[Callable[[dict[str, Any]], Any]] = []
_elicitation_result_hooks: list[Callable[[dict[str, Any]], Any]] = []
_notification_hooks: list[Callable[[dict[str, Any]], Any]] = []


def addElicitationHook(fn: Callable[[dict[str, Any]], Any]) -> Callable[[], None]:
    _elicitation_hooks.append(fn)

    def dispose() -> None:
        if fn in _elicitation_hooks:
            _elicitation_hooks.remove(fn)

    return dispose


def addElicitationResultHook(fn: Callable[[dict[str, Any]], Any]) -> Callable[[], None]:
    _elicitation_result_hooks.append(fn)

    def dispose() -> None:
        if fn in _elicitation_result_hooks:
            _elicitation_result_hooks.remove(fn)

    return dispose


def addNotificationHook(fn: Callable[[dict[str, Any]], Any]) -> Callable[[], None]:
    _notification_hooks.append(fn)

    def dispose() -> None:
        if fn in _notification_hooks:
            _notification_hooks.remove(fn)

    return dispose


async def _maybe_await(value: Any) -> Any:
    if asyncio.iscoroutine(value):
        return await value
    return value


def _get_mode(params: dict[str, Any]) -> str:
    return "url" if params.get("mode") == "url" else "form"


def _find_elicitation(queue: list[dict[str, Any]], server_name: str, elicitation_id: str) -> int:
    for index, event in enumerate(queue):
        params = event.get("params") or {}
        if (
            event.get("serverName") == server_name
            and params.get("mode") == "url"
            and params.get("elicitationId") == elicitation_id
        ):
            return index
    return -1


async def runElicitationHooks(
    serverName: str,
    params: dict[str, Any],
    signal: Any | None = None,
) -> dict[str, Any] | None:
    event = {
        "serverName": serverName,
        "message": params.get("message"),
        "requestedSchema": params.get("requestedSchema"),
        "signal": signal,
        "mode": _get_mode(params),
        "url": params.get("url"),
        "elicitationId": params.get("elicitationId"),
    }
    for hook in list(_elicitation_hooks):
        response = await _maybe_await(hook(event))
        if isinstance(response, dict) and response.get("blockingError"):
            return {"action": "decline"}
        if isinstance(response, dict) and response.get("elicitationResponse"):
            value = response["elicitationResponse"]
            return {"action": value.get("action"), "content": value.get("content")}
        if isinstance(response, dict) and response.get("action"):
            return {"action": response.get("action"), "content": response.get("content")}
    return None


async def runElicitationResultHooks(
    serverName: str,
    result: dict[str, Any],
    signal: Any | None = None,
    mode: str | None = None,
    elicitationId: str | None = None,
) -> dict[str, Any]:
    event = {
        "serverName": serverName,
        "action": result.get("action"),
        "content": result.get("content"),
        "signal": signal,
        "mode": mode,
        "elicitationId": elicitationId,
    }
    final = dict(result)
    for hook in list(_elicitation_result_hooks):
        response = await _maybe_await(hook(event))
        if isinstance(response, dict) and response.get("blockingError"):
            final = {"action": "decline"}
            break
        if isinstance(response, dict) and response.get("elicitationResultResponse"):
            value = response["elicitationResultResponse"]
            final = {"action": value.get("action"), "content": value.get("content", result.get("content"))}
            break
        if isinstance(response, dict) and response.get("action"):
            final = {"action": response.get("action"), "content": response.get("content", result.get("content"))}
            break
    notification = {
        "message": f'Elicitation response for server "{serverName}": {final.get("action")}',
        "notificationType": "elicitation_response",
    }
    for hook in list(_notification_hooks):
        await _maybe_await(hook(notification))
    return final


def registerElicitationHandler(
    client: Any,
    serverName: str,
    setAppState: Callable[[Callable[[dict[str, Any]], dict[str, Any]]], None],
) -> None:
    def request_handler(request: dict[str, Any], extra: Any | None = None) -> Any:
        async def run() -> dict[str, Any]:
            params = request.get("params") or {}
            signal = getattr(extra, "signal", None) if extra is not None else None
            hook_response = await runElicitationHooks(serverName, params, signal)
            if hook_response:
                return hook_response
            event: dict[str, Any] = {
                "serverName": serverName,
                "requestId": getattr(extra, "requestId", None) if extra is not None else None,
                "params": params,
                "signal": signal,
                "waitingState": {"actionLabel": "Skip confirmation"} if params.get("elicitationId") else None,
                "completed": False,
            }
            future: asyncio.Future[dict[str, Any]] = asyncio.get_running_loop().create_future()

            def respond(result: dict[str, Any]) -> None:
                if not future.done():
                    future.set_result(result)

            event["respond"] = respond

            def update(prev: dict[str, Any]) -> dict[str, Any]:
                queue = list(((prev.get("elicitation") or {}).get("queue")) or [])
                return {**prev, "elicitation": {"queue": [*queue, event]}}

            setAppState(update)
            raw = await future
            return await runElicitationResultHooks(serverName, raw, signal, _get_mode(params), params.get("elicitationId"))

        return run()

    def notification_handler(notification: dict[str, Any]) -> None:
        elicitation_id = (notification.get("params") or {}).get("elicitationId")

        def update(prev: dict[str, Any]) -> dict[str, Any]:
            queue = list(((prev.get("elicitation") or {}).get("queue")) or [])
            idx = _find_elicitation(queue, serverName, elicitation_id)
            if idx >= 0:
                queue[idx] = {**queue[idx], "completed": True}
            return {**prev, "elicitation": {"queue": queue}}

        setAppState(update)

    try:
        if hasattr(client, "setRequestHandler"):
            client.setRequestHandler("ElicitRequest", request_handler)
        if hasattr(client, "setNotificationHandler"):
            client.setNotificationHandler("ElicitationCompleteNotification", notification_handler)
    except Exception:
        return


__all__ = [
    "addElicitationHook",
    "addElicitationResultHook",
    "addNotificationHook",
    "registerElicitationHandler",
    "runElicitationHooks",
    "runElicitationResultHooks",
]
