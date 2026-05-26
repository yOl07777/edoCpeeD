"""Local OAuth authorization-code listener shim."""

from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse


@dataclass
class PendingResponse:
    status: int | None = None
    body: str = ""
    headers: dict[str, str] | None = None

    def writeHead(self, status: int, headers: dict[str, str] | None = None) -> None:
        self.status = status
        self.headers = headers or {}

    def end(self, body: str = "") -> None:
        self.body = body


class AuthCodeListener:
    def __init__(self, callbackPath: str = "/callback") -> None:
        self.callbackPath = callbackPath
        self.port = 0
        self.expectedState: str | None = None
        self.pendingResponse: PendingResponse | None = None
        self._future: asyncio.Future[str] | None = None
        self._closed = False

    async def start(self, port: int | None = None) -> int:
        if port:
            self.port = port
            return port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("localhost", 0))
            self.port = int(sock.getsockname()[1])
        return self.port

    def getPort(self) -> int:
        return self.port

    def hasPendingResponse(self) -> bool:
        return self.pendingResponse is not None

    async def waitForAuthorization(self, state: str, onReady: Callable[[], Any]) -> str:
        self.expectedState = state
        self._future = asyncio.get_running_loop().create_future()
        result = onReady()
        if asyncio.iscoroutine(result):
            await result
        return await self._future

    def handleRedirectUrl(self, url: str, response: PendingResponse | None = None) -> None:
        response = response or PendingResponse()
        parsed = urlparse(url)
        if parsed.path != self.callbackPath:
            response.writeHead(404)
            response.end()
            return
        params = parse_qs(parsed.query)
        auth_code = (params.get("code") or [None])[0]
        state = (params.get("state") or [None])[0]
        self.validateAndRespond(auth_code, state, response)

    def validateAndRespond(
        self,
        authCode: str | None,
        state: str | None,
        response: PendingResponse | None = None,
    ) -> None:
        response = response or PendingResponse()
        if not authCode:
            response.writeHead(400)
            response.end("Authorization code not found")
            self._reject(RuntimeError("No authorization code received"))
            return
        if state != self.expectedState:
            response.writeHead(400)
            response.end("Invalid state parameter")
            self._reject(RuntimeError("Invalid state parameter"))
            return
        self.pendingResponse = response
        self._resolve(authCode)

    def handleSuccessRedirect(
        self,
        scopes: list[str] | None = None,
        customHandler: Callable[[PendingResponse, list[str]], Any] | None = None,
    ) -> None:
        if not self.pendingResponse:
            return
        scopes = scopes or []
        if customHandler:
            customHandler(self.pendingResponse, scopes)
        else:
            success_url = "https://console.deepseek.com/success"
            self.pendingResponse.writeHead(302, {"Location": success_url})
            self.pendingResponse.end()
        self.pendingResponse = None

    def handleErrorRedirect(self) -> None:
        if not self.pendingResponse:
            return
        self.pendingResponse.writeHead(302, {"Location": "https://console.deepseek.com/error"})
        self.pendingResponse.end()
        self.pendingResponse = None

    def _resolve(self, authorizationCode: str) -> None:
        if self._future and not self._future.done():
            self._future.set_result(authorizationCode)

    def _reject(self, error: Exception) -> None:
        if self._future and not self._future.done():
            self._future.set_exception(error)

    def close(self) -> None:
        if self.pendingResponse:
            self.handleErrorRedirect()
        self._closed = True
        if self._future and not self._future.done():
            self._future.cancel()


__all__ = ["AuthCodeListener", "PendingResponse"]
