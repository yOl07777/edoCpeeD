"""MCP OAuth storage and provider helpers for the Python migration."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Awaitable, Callable


NONSTANDARD_INVALID_GRANT_ALIASES = {
    "invalid_refresh_token",
    "expired_refresh_token",
    "token_expired",
}


class AuthenticationCancelledError(Exception):
    def __init__(self) -> None:
        super().__init__("Authentication was cancelled")


@dataclass
class OAuthResponse:
    body: str
    status: int = 200
    statusText: str = "OK"
    headers: dict[str, str] | None = None

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300

    async def text(self) -> str:
        return self.body

    async def json(self) -> Any:
        return json.loads(self.body)


def _config_home() -> Path:
    return Path(os.getenv("DEEPCODE_CONFIG_HOME") or Path.home() / ".deepcode").resolve()


def _storage_path() -> Path:
    return Path(os.getenv("DEEPCODE_MCP_AUTH_STORE") or _config_home() / "mcp_oauth.json")


def _read_storage() -> dict[str, Any]:
    try:
        data = json.loads(_storage_path().read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_storage(data: dict[str, Any]) -> None:
    path = _storage_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _now_ms() -> int:
    return int(time.time() * 1000)


def _server_storage_entry(serverName: str, serverConfig: dict[str, Any]) -> tuple[dict[str, Any], str]:
    data = _read_storage()
    return data, getServerKey(serverName, serverConfig)


def getServerKey(serverName: str, serverConfig: dict[str, Any]) -> str:
    payload = {
        "type": serverConfig.get("type"),
        "url": serverConfig.get("url"),
        "headers": serverConfig.get("headers") or {},
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:16]
    return f"{serverName}|{digest}"


async def normalizeOAuthErrorBody(response: Any) -> Any:
    ok = bool(getattr(response, "ok", False))
    if not ok:
        return response
    text_method = getattr(response, "text", None)
    text = await text_method() if callable(text_method) else str(getattr(response, "body", ""))
    try:
        parsed = json.loads(text)
    except Exception:
        return OAuthResponse(text, getattr(response, "status", 200), getattr(response, "statusText", "OK"), getattr(response, "headers", None))
    if isinstance(parsed, dict) and parsed.get("access_token"):
        return OAuthResponse(text, getattr(response, "status", 200), getattr(response, "statusText", "OK"), getattr(response, "headers", None))
    if not isinstance(parsed, dict) or not isinstance(parsed.get("error"), str):
        return OAuthResponse(text, getattr(response, "status", 200), getattr(response, "statusText", "OK"), getattr(response, "headers", None))
    normalized = dict(parsed)
    if normalized["error"] in NONSTANDARD_INVALID_GRANT_ALIASES:
        original = normalized["error"]
        normalized["error"] = "invalid_grant"
        normalized.setdefault("error_description", f"Server returned non-standard error code: {original}")
    return OAuthResponse(json.dumps(normalized, ensure_ascii=False), 400, "Bad Request", getattr(response, "headers", None))


def hasMcpDiscoveryButNoToken(serverName: str, serverConfig: dict[str, Any]) -> bool:
    data, server_key = _server_storage_entry(serverName, serverConfig)
    entry = (data.get("mcpOAuth") or {}).get(server_key)
    return bool(entry is not None and not entry.get("accessToken") and not entry.get("refreshToken"))


def clearServerTokensFromLocalStorage(serverName: str, serverConfig: dict[str, Any]) -> None:
    data, server_key = _server_storage_entry(serverName, serverConfig)
    oauth = dict(data.get("mcpOAuth") or {})
    if server_key in oauth:
        oauth.pop(server_key, None)
        data["mcpOAuth"] = oauth
        _write_storage(data)


async def revokeServerTokens(
    serverName: str,
    serverConfig: dict[str, Any],
    options: dict[str, Any] | None = None,
) -> None:
    options = options or {}
    data, server_key = _server_storage_entry(serverName, serverConfig)
    token_data = (data.get("mcpOAuth") or {}).get(server_key)
    preserved: dict[str, Any] = {}
    if options.get("preserveStepUpState") and token_data:
        for key in ("stepUpScope", "discoveryState"):
            if token_data.get(key) is not None:
                preserved[key] = token_data[key]
    clearServerTokensFromLocalStorage(serverName, serverConfig)
    if preserved:
        fresh = _read_storage()
        fresh.setdefault("mcpOAuth", {})[server_key] = {
            "serverName": serverName,
            "serverUrl": serverConfig.get("url"),
            "accessToken": "",
            "expiresAt": 0,
            **preserved,
        }
        _write_storage(fresh)


def saveMcpClientSecret(serverName: str, serverConfig: dict[str, Any], clientSecret: str) -> None:
    data, server_key = _server_storage_entry(serverName, serverConfig)
    data.setdefault("mcpOAuthClientConfig", {})[server_key] = {"clientSecret": clientSecret}
    _write_storage(data)


def clearMcpClientConfig(serverName: str, serverConfig: dict[str, Any]) -> None:
    data, server_key = _server_storage_entry(serverName, serverConfig)
    configs = dict(data.get("mcpOAuthClientConfig") or {})
    if server_key in configs:
        configs.pop(server_key, None)
        data["mcpOAuthClientConfig"] = configs
        _write_storage(data)


def getMcpClientConfig(serverName: str, serverConfig: dict[str, Any]) -> dict[str, Any] | None:
    data, server_key = _server_storage_entry(serverName, serverConfig)
    value = (data.get("mcpOAuthClientConfig") or {}).get(server_key)
    return dict(value) if isinstance(value, dict) else None


async def readClientSecret() -> str:
    secret = os.getenv("MCP_CLIENT_SECRET")
    if secret:
        return secret
    raise RuntimeError("No TTY prompt is available in the Python migration. Set MCP_CLIENT_SECRET instead.")


async def performMCPOAuthFlow(*_: Any, **__: Any) -> None:
    raise AuthenticationCancelledError()


def wrapFetchWithStepUpDetection(fetchFn: Callable[..., Awaitable[Any]] | Callable[..., Any], provider: Any | None = None) -> Callable[..., Awaitable[Any]]:
    async def wrapped(*args: Any, **kwargs: Any) -> Any:
        result = fetchFn(*args, **kwargs)
        if asyncio.iscoroutine(result):
            result = await result
        status = getattr(result, "status", None)
        if status == 403 and provider and hasattr(provider, "markStepUpPending"):
            text = ""
            text_method = getattr(result, "text", None)
            if callable(text_method):
                try:
                    text = await text_method()
                except Exception:
                    text = ""
            if "insufficient_scope" in text:
                provider.markStepUpPending(" ".join(text.split()))
        return result

    return wrapped


class ClaudeAuthProvider:
    def __init__(
        self,
        serverName: str,
        serverConfig: dict[str, Any],
        redirectUri: str = "http://127.0.0.1/callback",
        handleRedirection: bool = False,
        onAuthorizationUrl: Callable[[str], None] | None = None,
        skipBrowserOpen: bool | None = False,
    ) -> None:
        self.serverName = serverName
        self.serverConfig = serverConfig
        self.redirectUri = redirectUri
        self.handleRedirection = handleRedirection
        self.onAuthorizationUrlCallback = onAuthorizationUrl
        self.skipBrowserOpen = bool(skipBrowserOpen)
        self._authorizationUrl: str | None = None
        self._state: str | None = None
        self._pendingStepUpScope: str | None = None
        self._metadata: dict[str, Any] | None = None

    @property
    def redirectUrl(self) -> str:
        return self.redirectUri

    @property
    def authorizationUrl(self) -> str | None:
        return self._authorizationUrl

    @property
    def clientMetadata(self) -> dict[str, Any]:
        metadata = {
            "client_name": f"DeepSeek Code ({self.serverName})",
            "redirect_uris": [self.redirectUri],
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "none",
        }
        scope = self._scope_from_metadata()
        if scope:
            metadata["scope"] = scope
        return metadata

    @property
    def clientMetadataUrl(self) -> str | None:
        return os.getenv("MCP_OAUTH_CLIENT_METADATA_URL") or os.getenv("DEEPCODE_MCP_CLIENT_METADATA_URL")

    def setMetadata(self, metadata: dict[str, Any] | None) -> None:
        self._metadata = metadata

    def markStepUpPending(self, scope: str) -> None:
        self._pendingStepUpScope = scope

    async def state(self) -> str:
        if not self._state:
            self._state = os.urandom(32).hex()
        return self._state

    async def clientInformation(self) -> dict[str, Any] | None:
        data, server_key = _server_storage_entry(self.serverName, self.serverConfig)
        stored = (data.get("mcpOAuth") or {}).get(server_key)
        if isinstance(stored, dict) and stored.get("clientId"):
            return {"client_id": stored.get("clientId"), "client_secret": stored.get("clientSecret")}
        config_client_id = (self.serverConfig.get("oauth") or {}).get("clientId")
        if config_client_id:
            client_config = (data.get("mcpOAuthClientConfig") or {}).get(server_key) or {}
            return {"client_id": config_client_id, "client_secret": client_config.get("clientSecret")}
        return None

    async def saveClientInformation(self, clientInformation: dict[str, Any]) -> None:
        data, server_key = _server_storage_entry(self.serverName, self.serverConfig)
        current = (data.get("mcpOAuth") or {}).get(server_key) or {}
        data.setdefault("mcpOAuth", {})[server_key] = {
            **current,
            "serverName": self.serverName,
            "serverUrl": self.serverConfig.get("url"),
            "clientId": clientInformation.get("client_id"),
            "clientSecret": clientInformation.get("client_secret"),
            "accessToken": current.get("accessToken", ""),
            "expiresAt": current.get("expiresAt", 0),
        }
        _write_storage(data)

    async def tokens(self) -> dict[str, Any] | None:
        data, server_key = _server_storage_entry(self.serverName, self.serverConfig)
        token_data = (data.get("mcpOAuth") or {}).get(server_key)
        if not token_data:
            return None
        expires_in = int((int(token_data.get("expiresAt") or 0) - _now_ms()) / 1000)
        if expires_in <= 0 and not token_data.get("refreshToken"):
            return None
        current_scopes = str(token_data.get("scope") or "").split()
        needs_step_up = bool(
            self._pendingStepUpScope
            and any(scope not in current_scopes for scope in self._pendingStepUpScope.split())
        )
        return {
            "access_token": token_data.get("accessToken"),
            "refresh_token": None if needs_step_up else token_data.get("refreshToken"),
            "expires_in": expires_in,
            "scope": token_data.get("scope"),
            "token_type": "Bearer",
        }

    async def saveTokens(self, tokens: dict[str, Any]) -> None:
        self._pendingStepUpScope = None
        data, server_key = _server_storage_entry(self.serverName, self.serverConfig)
        current = (data.get("mcpOAuth") or {}).get(server_key) or {}
        data.setdefault("mcpOAuth", {})[server_key] = {
            **current,
            "serverName": self.serverName,
            "serverUrl": self.serverConfig.get("url"),
            "accessToken": tokens.get("access_token"),
            "refreshToken": tokens.get("refresh_token"),
            "expiresAt": _now_ms() + int(tokens.get("expires_in") or 3600) * 1000,
            "scope": tokens.get("scope"),
        }
        _write_storage(data)

    async def invalidateCredentials(self, scope: str) -> None:
        data, server_key = _server_storage_entry(self.serverName, self.serverConfig)
        if scope in {"all", "tokens"}:
            oauth = data.get("mcpOAuth") or {}
            if server_key in oauth:
                if scope == "all":
                    oauth.pop(server_key, None)
                else:
                    oauth[server_key].pop("accessToken", None)
                    oauth[server_key].pop("refreshToken", None)
                    oauth[server_key]["expiresAt"] = 0
                data["mcpOAuth"] = oauth
        if scope in {"all", "client"}:
            configs = data.get("mcpOAuthClientConfig") or {}
            configs.pop(server_key, None)
            data["mcpOAuthClientConfig"] = configs
        _write_storage(data)

    def _scope_from_metadata(self) -> str | None:
        metadata = self._metadata or {}
        if isinstance(metadata.get("scope"), str):
            return metadata["scope"]
        if isinstance(metadata.get("default_scope"), str):
            return metadata["default_scope"]
        if isinstance(metadata.get("scopes_supported"), list):
            return " ".join(str(scope) for scope in metadata["scopes_supported"])
        return None


__all__ = [
    "AuthenticationCancelledError",
    "ClaudeAuthProvider",
    "OAuthResponse",
    "clearMcpClientConfig",
    "clearServerTokensFromLocalStorage",
    "getMcpClientConfig",
    "getServerKey",
    "hasMcpDiscoveryButNoToken",
    "normalizeOAuthErrorBody",
    "performMCPOAuthFlow",
    "readClientSecret",
    "revokeServerTokens",
    "saveMcpClientSecret",
    "wrapFetchWithStepUpDetection",
]
