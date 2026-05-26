"""OAuth client helpers for the DeepSeek/Python migration."""

from __future__ import annotations

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlencode

from .getOauthProfile import getOauthProfileFromOauthToken

CLAUDE_AI_INFERENCE_SCOPE = "org:create_api_key"
DEFAULT_OAUTH_SCOPES = [
    "user:profile",
    "user:inference",
    "org:create_api_key",
    "user:mcp_servers",
]


def _config_home() -> Path:
    return Path(os.getenv("DEEPCODE_CONFIG_HOME") or Path.home() / ".deepcode").resolve()


def _config_path() -> Path:
    return _config_home() / "config.json"


def _read_config() -> dict[str, Any]:
    try:
        data = json.loads(_config_path().read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_config(data: dict[str, Any]) -> None:
    _config_path().parent.mkdir(parents=True, exist_ok=True)
    _config_path().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _oauth_config() -> dict[str, str]:
    base = os.getenv("DEEPCODE_OAUTH_BASE_API_URL") or os.getenv("DEEPSEEK_OAUTH_BASE_API_URL") or "https://console.deepseek.com"
    return {
        "CLIENT_ID": os.getenv("DEEPCODE_OAUTH_CLIENT_ID") or os.getenv("DEEPSEEK_OAUTH_CLIENT_ID") or "deepseek-code",
        "CONSOLE_AUTHORIZE_URL": os.getenv("DEEPCODE_CONSOLE_AUTHORIZE_URL") or f"{base.rstrip('/')}/oauth/authorize",
        "CLAUDE_AI_AUTHORIZE_URL": os.getenv("DEEPCODE_AI_AUTHORIZE_URL") or f"{base.rstrip('/')}/oauth/authorize",
        "TOKEN_URL": os.getenv("DEEPCODE_OAUTH_TOKEN_URL") or f"{base.rstrip('/')}/oauth/token",
        "ROLES_URL": os.getenv("DEEPCODE_OAUTH_ROLES_URL") or f"{base.rstrip('/')}/api/oauth/roles",
        "API_KEY_URL": os.getenv("DEEPCODE_OAUTH_API_KEY_URL") or f"{base.rstrip('/')}/api/oauth/api_key",
        "MANUAL_REDIRECT_URL": os.getenv("DEEPCODE_OAUTH_MANUAL_REDIRECT_URL") or "urn:ietf:wg:oauth:2.0:oob",
    }


async def _maybe_await(value: Any) -> Any:
    if asyncio.iscoroutine(value):
        return await value
    return value


async def _json_response(response: Any) -> Any:
    if isinstance(response, dict):
        return response
    if hasattr(response, "json"):
        return await _maybe_await(response.json())
    if hasattr(response, "text"):
        return json.loads(await _maybe_await(response.text()))
    return response


def shouldUseClaudeAIAuth(scopes: list[str] | None) -> bool:
    return bool(scopes and CLAUDE_AI_INFERENCE_SCOPE in scopes)


def parseScopes(scopeString: str | None = None) -> list[str]:
    return [scope for scope in str(scopeString or "").split(" ") if scope]


def buildAuthUrl(params: dict[str, Any] | None = None, **kwargs: Any) -> str:
    merged = dict(params or {})
    merged.update(kwargs)
    cfg = _oauth_config()
    base = cfg["CLAUDE_AI_AUTHORIZE_URL"] if merged.get("loginWithClaudeAi") else cfg["CONSOLE_AUTHORIZE_URL"]
    scopes = [CLAUDE_AI_INFERENCE_SCOPE] if merged.get("inferenceOnly") else DEFAULT_OAUTH_SCOPES
    query = {
        "code": "true",
        "client_id": cfg["CLIENT_ID"],
        "response_type": "code",
        "redirect_uri": cfg["MANUAL_REDIRECT_URL"] if merged.get("isManual") else f"http://localhost:{int(merged.get('port') or 0)}/callback",
        "scope": " ".join(scopes),
        "code_challenge": merged["codeChallenge"],
        "code_challenge_method": "S256",
        "state": merged["state"],
    }
    for key in ("orgUUID", "loginHint", "loginMethod"):
        value = merged.get(key)
        if value:
            query_key = {"orgUUID": "orgUUID", "loginHint": "login_hint", "loginMethod": "login_method"}[key]
            query[query_key] = value
    return base + ("&" if "?" in base else "?") + urlencode(query)


async def exchangeCodeForTokens(
    authorizationCode: str,
    state: str,
    codeVerifier: str,
    port: int,
    useManualRedirect: bool = False,
    expiresIn: int | None = None,
    *,
    http_post: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    if not http_post:
        raise RuntimeError("exchangeCodeForTokens requires an injected http_post in the Python migration")
    cfg = _oauth_config()
    body: dict[str, Any] = {
        "grant_type": "authorization_code",
        "code": authorizationCode,
        "redirect_uri": cfg["MANUAL_REDIRECT_URL"] if useManualRedirect else f"http://localhost:{port}/callback",
        "client_id": cfg["CLIENT_ID"],
        "code_verifier": codeVerifier,
        "state": state,
    }
    if expiresIn is not None:
        body["expires_in"] = expiresIn
    response = await _maybe_await(http_post(cfg["TOKEN_URL"], json=body, headers={"Content-Type": "application/json"}, timeout=15))
    return await _json_response(response)


async def refreshOAuthToken(
    refreshToken: str,
    options: dict[str, Any] | None = None,
    *,
    http_post: Callable[..., Any] | None = None,
    http_get: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    if not http_post:
        raise RuntimeError("refreshOAuthToken requires an injected http_post in the Python migration")
    requested_scopes = (options or {}).get("scopes") or DEFAULT_OAUTH_SCOPES
    cfg = _oauth_config()
    body = {
        "grant_type": "refresh_token",
        "refresh_token": refreshToken,
        "client_id": cfg["CLIENT_ID"],
        "scope": " ".join(requested_scopes),
    }
    data = await _json_response(
        await _maybe_await(http_post(cfg["TOKEN_URL"], json=body, headers={"Content-Type": "application/json"}, timeout=15))
    )
    access_token = data.get("access_token")
    profile_info = await fetchProfileInfo(access_token, http_get=http_get) if access_token and http_get else None
    return {
        "accessToken": access_token,
        "refreshToken": data.get("refresh_token") or refreshToken,
        "expiresAt": int(time.time() * 1000) + int(data.get("expires_in") or 3600) * 1000,
        "scopes": parseScopes(data.get("scope")),
        "subscriptionType": (profile_info or {}).get("subscriptionType"),
        "rateLimitTier": (profile_info or {}).get("rateLimitTier"),
        "profile": (profile_info or {}).get("rawProfile"),
        "tokenAccount": {
            "uuid": ((data.get("account") or {}).get("uuid")),
            "emailAddress": ((data.get("account") or {}).get("email_address")),
            "organizationUuid": ((data.get("organization") or {}).get("uuid")),
        }
        if data.get("account")
        else None,
    }


async def fetchAndStoreUserRoles(accessToken: str, *, http_get: Callable[..., Any] | None = None) -> None:
    if not http_get:
        return None
    cfg = _oauth_config()
    data = await _json_response(
        await _maybe_await(http_get(cfg["ROLES_URL"], headers={"Authorization": f"Bearer {accessToken}"}, timeout=10))
    )
    config = _read_config()
    account = dict(config.get("oauthAccount") or {})
    account.update(
        {
            "organizationRole": data.get("organization_role"),
            "workspaceRole": data.get("workspace_role"),
            "organizationName": data.get("organization_name"),
        }
    )
    config["oauthAccount"] = account
    _write_config(config)


async def createAndStoreApiKey(accessToken: str, *, http_post: Callable[..., Any] | None = None) -> str | None:
    if not http_post:
        return None
    cfg = _oauth_config()
    data = await _json_response(
        await _maybe_await(http_post(cfg["API_KEY_URL"], headers={"Authorization": f"Bearer {accessToken}"}, timeout=10))
    )
    api_key = data.get("raw_key")
    if api_key:
        config = _read_config()
        config["apiKey"] = api_key
        _write_config(config)
    return api_key


def isOAuthTokenExpired(expiresAt: int | None) -> bool:
    if expiresAt is None:
        return False
    return int(time.time() * 1000) + 5 * 60 * 1000 >= int(expiresAt)


async def fetchProfileInfo(accessToken: str, *, http_get: Callable[..., Any] | None = None) -> dict[str, Any]:
    profile = await getOauthProfileFromOauthToken(accessToken, http_get=http_get)
    org = (profile or {}).get("organization") or {}
    account = (profile or {}).get("account") or {}
    org_type = org.get("organization_type")
    subscription = {
        "claude_max": "max",
        "claude_pro": "pro",
        "claude_enterprise": "enterprise",
        "claude_team": "team",
    }.get(org_type)
    result = {
        "subscriptionType": subscription,
        "rateLimitTier": org.get("rate_limit_tier"),
        "hasExtraUsageEnabled": org.get("has_extra_usage_enabled"),
        "billingType": org.get("billing_type"),
        "rawProfile": profile,
    }
    if account.get("display_name"):
        result["displayName"] = account["display_name"]
    if account.get("created_at"):
        result["accountCreatedAt"] = account["created_at"]
    if org.get("subscription_created_at"):
        result["subscriptionCreatedAt"] = org["subscription_created_at"]
    return result


async def getOrganizationUUID(*, http_get: Callable[..., Any] | None = None) -> str | None:
    config = _read_config()
    org_uuid = (config.get("oauthAccount") or {}).get("organizationUuid")
    if org_uuid:
        return org_uuid
    token = os.getenv("DEEPCODE_OAUTH_ACCESS_TOKEN")
    if not token or not http_get:
        return None
    profile = await getOauthProfileFromOauthToken(token, http_get=http_get)
    return ((profile or {}).get("organization") or {}).get("uuid")


async def populateOAuthAccountInfoIfNeeded(*, http_get: Callable[..., Any] | None = None) -> bool:
    env_account = os.getenv("CLAUDE_CODE_ACCOUNT_UUID") or os.getenv("DEEPCODE_ACCOUNT_UUID")
    env_email = os.getenv("CLAUDE_CODE_USER_EMAIL") or os.getenv("DEEPCODE_USER_EMAIL")
    env_org = os.getenv("CLAUDE_CODE_ORGANIZATION_UUID") or os.getenv("DEEPCODE_ORGANIZATION_UUID")
    if env_account and env_email and env_org:
        storeOAuthAccountInfo({"accountUuid": env_account, "emailAddress": env_email, "organizationUuid": env_org})
        return True
    token = os.getenv("DEEPCODE_OAUTH_ACCESS_TOKEN")
    if token and http_get:
        profile = await getOauthProfileFromOauthToken(token, http_get=http_get)
        if profile:
            account = profile.get("account") or {}
            org = profile.get("organization") or {}
            storeOAuthAccountInfo(
                {
                    "accountUuid": account.get("uuid"),
                    "emailAddress": account.get("email"),
                    "organizationUuid": org.get("uuid"),
                    "displayName": account.get("display_name"),
                    "hasExtraUsageEnabled": org.get("has_extra_usage_enabled"),
                    "billingType": org.get("billing_type"),
                    "accountCreatedAt": account.get("created_at"),
                    "subscriptionCreatedAt": org.get("subscription_created_at"),
                }
            )
            return True
    return False


def storeOAuthAccountInfo(info: dict[str, Any] | None = None, **kwargs: Any) -> None:
    data = dict(info or {})
    data.update(kwargs)
    account = {
        "accountUuid": data.get("accountUuid"),
        "emailAddress": data.get("emailAddress"),
        "organizationUuid": data.get("organizationUuid"),
        "hasExtraUsageEnabled": data.get("hasExtraUsageEnabled"),
        "billingType": data.get("billingType"),
        "accountCreatedAt": data.get("accountCreatedAt"),
        "subscriptionCreatedAt": data.get("subscriptionCreatedAt"),
    }
    if data.get("displayName"):
        account["displayName"] = data["displayName"]
    config = _read_config()
    if config.get("oauthAccount") != account:
        config["oauthAccount"] = account
        _write_config(config)


__all__ = [
    "buildAuthUrl",
    "createAndStoreApiKey",
    "exchangeCodeForTokens",
    "fetchAndStoreUserRoles",
    "fetchProfileInfo",
    "getOrganizationUUID",
    "isOAuthTokenExpired",
    "parseScopes",
    "populateOAuthAccountInfoIfNeeded",
    "refreshOAuthToken",
    "shouldUseClaudeAIAuth",
    "storeOAuthAccountInfo",
]
