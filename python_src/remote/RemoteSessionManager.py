"""Remote session manager shim without implicit network side effects."""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Awaitable

RemotePermissionResponse = dict[str, Any]
RemoteSessionConfig = dict[str, Any]
RemoteSessionCallbacks = dict[str, Callable[..., Any]]


def _maybe_call(callback: Callable[..., Any] | None, *args: Any) -> Any:
    if callback:
        return callback(*args)
    return None


class RemoteSessionManager:
    def __init__(
        self,
        config: RemoteSessionConfig,
        callbacks: RemoteSessionCallbacks | None = None,
        *,
        websocket: Any | None = None,
        send_event: Callable[[str, Any, dict[str, Any] | None], Awaitable[bool] | bool] | None = None,
    ) -> None:
        self.config = config
        self.callbacks = callbacks or {}
        self.websocket = websocket
        self.send_event = send_event
        self.pendingPermissionRequests: dict[str, dict[str, Any]] = {}
        self._connected = False

    def connect(self) -> None:
        self._connected = True
        if self.websocket and hasattr(self.websocket, "connect"):
            result = self.websocket.connect()
            if asyncio.iscoroutine(result):
                asyncio.create_task(result)
        _maybe_call(self.callbacks.get("onConnected"))

    def handleMessage(self, message: dict[str, Any]) -> None:
        message_type = message.get("type")
        if message_type == "control_request":
            self._handle_control_request(message)
            return
        if message_type == "control_cancel_request":
            request_id = message.get("request_id")
            pending = self.pendingPermissionRequests.pop(request_id, None)
            _maybe_call(
                self.callbacks.get("onPermissionCancelled"),
                request_id,
                (pending or {}).get("tool_use_id"),
            )
            return
        if message_type == "control_response":
            return
        _maybe_call(self.callbacks.get("onMessage"), message)

    def _handle_control_request(self, request: dict[str, Any]) -> None:
        request_id = request.get("request_id")
        inner = request.get("request") or {}
        if inner.get("subtype") == "can_use_tool":
            self.pendingPermissionRequests[request_id] = inner
            _maybe_call(self.callbacks.get("onPermissionRequest"), inner, request_id)
            return
        response = {
            "type": "control_response",
            "response": {
                "subtype": "error",
                "request_id": request_id,
                "error": f"Unsupported control request subtype: {inner.get('subtype')}",
            },
        }
        if self.websocket and hasattr(self.websocket, "sendControlResponse"):
            self.websocket.sendControlResponse(response)

    async def sendMessage(self, content: Any, opts: dict[str, Any] | None = None) -> bool:
        if not self.send_event:
            return False
        result = self.send_event(self.config["sessionId"], content, opts)
        if asyncio.iscoroutine(result):
            result = await result
        return bool(result)

    def respondToPermissionRequest(self, requestId: str, result: RemotePermissionResponse) -> None:
        if requestId not in self.pendingPermissionRequests:
            return
        self.pendingPermissionRequests.pop(requestId, None)
        response_payload = {
            "behavior": result.get("behavior"),
            **(
                {"updatedInput": result.get("updatedInput", {})}
                if result.get("behavior") == "allow"
                else {"message": result.get("message", "")}
            ),
        }
        response = {
            "type": "control_response",
            "response": {
                "subtype": "success",
                "request_id": requestId,
                "response": response_payload,
            },
        }
        if self.websocket and hasattr(self.websocket, "sendControlResponse"):
            self.websocket.sendControlResponse(response)

    def isConnected(self) -> bool:
        if self.websocket and hasattr(self.websocket, "isConnected"):
            return bool(self.websocket.isConnected())
        return self._connected

    def cancelSession(self) -> None:
        if self.websocket and hasattr(self.websocket, "sendControlRequest"):
            self.websocket.sendControlRequest({"subtype": "interrupt"})

    def getSessionId(self) -> str:
        return str(self.config.get("sessionId", ""))

    def disconnect(self) -> None:
        if self.websocket and hasattr(self.websocket, "close"):
            self.websocket.close()
        self.websocket = None
        self._connected = False
        self.pendingPermissionRequests.clear()

    def reconnect(self) -> None:
        if self.websocket and hasattr(self.websocket, "reconnect"):
            self.websocket.reconnect()
        else:
            self.connect()


def createRemoteSessionConfig(
    sessionId: str,
    getAccessToken: Callable[[], str],
    orgUuid: str,
    hasInitialPrompt: bool = False,
    viewerOnly: bool = False,
) -> RemoteSessionConfig:
    return {
        "sessionId": sessionId,
        "getAccessToken": getAccessToken,
        "orgUuid": orgUuid,
        "hasInitialPrompt": hasInitialPrompt,
        "viewerOnly": viewerOnly,
    }


__all__ = ["RemoteSessionManager", "createRemoteSessionConfig"]
