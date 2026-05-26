"""HTTP client for bridge environment/session APIs."""

from __future__ import annotations

import re
from typing import Any, Awaitable, Callable

import httpx

from .debugUtils import extractErrorDetail
from .types import BRIDGE_LOGIN_INSTRUCTION

SAFE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


class BridgeFatalError(RuntimeError):
    def __init__(self, message: str, status: int, errorType: str | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.errorType = errorType


def validateBridgeId(id: str, label: str) -> str:
    if not id or not SAFE_ID_PATTERN.fullmatch(id):
        raise ValueError(f"Invalid {label}: contains unsafe characters")
    return id


def isExpiredErrorType(errorType: str | None) -> bool:
    return bool(errorType and ("expired" in errorType or "lifetime" in errorType))


def isSuppressible403(err: BridgeFatalError) -> bool:
    return err.status == 403 and (
        "external_poll_sessions" in str(err) or "environments:manage" in str(err)
    )


def _extract_error_type(data: Any) -> str | None:
    if isinstance(data, dict):
        error = data.get("error")
        if isinstance(error, dict) and isinstance(error.get("type"), str):
            return error["type"]
    return None


def _handle_error_status(status: int, data: Any, context: str) -> None:
    if status in {200, 204}:
        return
    detail = extractErrorDetail(data)
    error_type = _extract_error_type(data)
    if status == 401:
        raise BridgeFatalError(
            f"{context}: Authentication failed (401){': ' + detail if detail else ''}. {BRIDGE_LOGIN_INSTRUCTION}",
            401,
            error_type,
        )
    if status == 403:
        message = (
            "Remote Control session has expired. Please restart."
            if isExpiredErrorType(error_type)
            else f"{context}: Access denied (403){': ' + detail if detail else ''}. Check your organization permissions."
        )
        raise BridgeFatalError(message, 403, error_type)
    if status == 404:
        raise BridgeFatalError(detail or f"{context}: Not found (404).", 404, error_type)
    if status == 410:
        raise BridgeFatalError(
            detail or "Remote Control session has expired. Please restart.",
            410,
            error_type or "environment_expired",
        )
    if status == 429:
        raise RuntimeError(f"{context}: Rate limited (429). Polling too frequently.")
    raise RuntimeError(f"{context}: Failed with status {status}{': ' + detail if detail else ''}")


class BridgeApiClient:
    def __init__(
        self,
        *,
        baseUrl: str,
        getAccessToken: Callable[[], str | None],
        runnerVersion: str = "python",
        onDebug: Callable[[str], None] | None = None,
        onAuth401: Callable[[str], Awaitable[bool]] | None = None,
        getTrustedDeviceToken: Callable[[], str | None] | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.baseUrl = baseUrl.rstrip("/")
        self.getAccessToken = getAccessToken
        self.runnerVersion = runnerVersion
        self.onDebug = onDebug
        self.onAuth401 = onAuth401
        self.getTrustedDeviceToken = getTrustedDeviceToken
        self.client = client
        self._consecutive_empty_polls = 0

    def _debug(self, message: str) -> None:
        if self.onDebug:
            self.onDebug(message)

    def _headers(self, token: str) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "x-environment-runner-version": self.runnerVersion,
        }
        device_token = self.getTrustedDeviceToken() if self.getTrustedDeviceToken else None
        if device_token:
            headers["X-Trusted-Device-Token"] = device_token
        return headers

    def _resolve_auth(self) -> str:
        token = self.getAccessToken()
        if not token:
            raise RuntimeError(BRIDGE_LOGIN_INSTRUCTION)
        return token

    async def _request(self, method: str, path: str, *, token: str, **kwargs: Any) -> httpx.Response:
        owns_client = self.client is None
        client = self.client or httpx.AsyncClient(timeout=15.0)
        try:
            return await client.request(method, self.baseUrl + path, headers=self._headers(token), **kwargs)
        finally:
            if owns_client:
                await client.aclose()

    async def _oauth_request(self, method: str, path: str, context: str, **kwargs: Any) -> httpx.Response:
        token = self._resolve_auth()
        response = await self._request(method, path, token=token, **kwargs)
        if response.status_code != 401 or not self.onAuth401:
            return response
        if await self.onAuth401(token):
            response = await self._request(method, path, token=self._resolve_auth(), **kwargs)
        return response

    async def registerBridgeEnvironment(self, config: dict[str, Any]) -> dict[str, Any]:
        body = {
            "machine_name": config.get("machineName"),
            "directory": config.get("dir"),
            "branch": config.get("branch"),
            "git_repo_url": config.get("gitRepoUrl"),
            "max_sessions": config.get("maxSessions"),
            "metadata": {"worker_type": config.get("workerType", "deepseek_code")},
        }
        if config.get("reuseEnvironmentId"):
            body["environment_id"] = config["reuseEnvironmentId"]
        response = await self._oauth_request("POST", "/v1/environments/bridge", "Registration", json=body)
        data = _json_or_none(response)
        _handle_error_status(response.status_code, data, "Registration")
        return data or {}

    async def pollForWork(self, environmentId: str, environmentSecret: str, signal: Any = None, reclaimOlderThanMs: int | None = None) -> dict[str, Any] | None:
        validateBridgeId(environmentId, "environmentId")
        params = {"reclaim_older_than_ms": reclaimOlderThanMs} if reclaimOlderThanMs is not None else None
        response = await self._request("GET", f"/v1/environments/{environmentId}/work/poll", token=environmentSecret, params=params)
        data = _json_or_none(response)
        _handle_error_status(response.status_code, data, "Poll")
        if not data:
            self._consecutive_empty_polls += 1
            return None
        self._consecutive_empty_polls = 0
        return data

    async def acknowledgeWork(self, environmentId: str, workId: str, sessionToken: str) -> None:
        validateBridgeId(environmentId, "environmentId")
        validateBridgeId(workId, "workId")
        response = await self._request("POST", f"/v1/environments/{environmentId}/work/{workId}/ack", token=sessionToken, json={})
        _handle_error_status(response.status_code, _json_or_none(response), "Acknowledge")

    async def stopWork(self, environmentId: str, workId: str, force: bool) -> None:
        validateBridgeId(environmentId, "environmentId")
        validateBridgeId(workId, "workId")
        response = await self._oauth_request("POST", f"/v1/environments/{environmentId}/work/{workId}/stop", "StopWork", json={"force": force})
        _handle_error_status(response.status_code, _json_or_none(response), "StopWork")

    async def deregisterEnvironment(self, environmentId: str) -> None:
        validateBridgeId(environmentId, "environmentId")
        response = await self._oauth_request("DELETE", f"/v1/environments/bridge/{environmentId}", "Deregister")
        _handle_error_status(response.status_code, _json_or_none(response), "Deregister")

    async def archiveSession(self, sessionId: str) -> None:
        validateBridgeId(sessionId, "sessionId")
        response = await self._oauth_request("POST", f"/v1/sessions/{sessionId}/archive", "ArchiveSession", json={})
        if response.status_code == 409:
            return
        _handle_error_status(response.status_code, _json_or_none(response), "ArchiveSession")

    async def reconnectSession(self, environmentId: str, sessionId: str) -> None:
        validateBridgeId(environmentId, "environmentId")
        validateBridgeId(sessionId, "sessionId")
        response = await self._oauth_request("POST", f"/v1/environments/{environmentId}/bridge/reconnect", "ReconnectSession", json={"session_id": sessionId})
        _handle_error_status(response.status_code, _json_or_none(response), "ReconnectSession")

    async def heartbeatWork(self, environmentId: str, workId: str, sessionToken: str) -> dict[str, Any]:
        validateBridgeId(environmentId, "environmentId")
        validateBridgeId(workId, "workId")
        response = await self._request("POST", f"/v1/environments/{environmentId}/work/{workId}/heartbeat", token=sessionToken, json={})
        data = _json_or_none(response)
        _handle_error_status(response.status_code, data, "Heartbeat")
        return data or {}

    async def sendPermissionResponseEvent(self, sessionId: str, event: dict[str, Any], sessionToken: str) -> None:
        validateBridgeId(sessionId, "sessionId")
        response = await self._request("POST", f"/v1/sessions/{sessionId}/events", token=sessionToken, json={"events": [event]})
        _handle_error_status(response.status_code, _json_or_none(response), "SendPermissionResponseEvent")


def _json_or_none(response: httpx.Response) -> Any:
    if not response.content:
        return None
    try:
        return response.json()
    except ValueError:
        return None


def createBridgeApiClient(deps: dict[str, Any] | None = None, **kwargs: Any) -> BridgeApiClient:
    merged = dict(deps or {})
    merged.update(kwargs)
    return BridgeApiClient(**merged)
