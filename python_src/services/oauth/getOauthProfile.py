"""OAuth profile fetch helpers with injectable HTTP clients."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Callable


def _base_api_url() -> str:
    return os.getenv("DEEPCODE_OAUTH_BASE_API_URL") or os.getenv("DEEPSEEK_OAUTH_BASE_API_URL") or "https://console.deepseek.com"


def _config_home() -> Path:
    return Path(os.getenv("DEEPCODE_CONFIG_HOME") or Path.home() / ".deepcode").resolve()


def _read_config() -> dict[str, Any]:
    try:
        data = json.loads((_config_home() / "config.json").read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


async def _maybe_await(value: Any) -> Any:
    if asyncio.iscoroutine(value):
        return await value
    return value


async def _json_response(response: Any) -> Any:
    if isinstance(response, dict):
        return response
    if hasattr(response, "json"):
        value = response.json()
        return await _maybe_await(value)
    if hasattr(response, "text"):
        text = response.text()
        return json.loads(await _maybe_await(text))
    return response


async def getOauthProfileFromApiKey(
    apiKey: str | None = None,
    accountUuid: str | None = None,
    *,
    http_get: Callable[..., Any] | None = None,
) -> dict[str, Any] | None:
    config = _read_config()
    account_uuid = accountUuid or (config.get("oauthAccount") or {}).get("accountUuid")
    api_key = apiKey or os.getenv("DEEPSEEK_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not account_uuid or not api_key or not http_get:
        return None
    endpoint = f"{_base_api_url().rstrip('/')}/api/claude_cli_profile"
    response = await _maybe_await(
        http_get(
            endpoint,
            headers={"x-api-key": api_key, "anthropic-beta": "oauth-2025-04-20"},
            params={"account_uuid": account_uuid},
            timeout=10,
        )
    )
    return await _json_response(response)


async def getOauthProfileFromOauthToken(
    accessToken: str,
    *,
    http_get: Callable[..., Any] | None = None,
) -> dict[str, Any] | None:
    if not accessToken or not http_get:
        return None
    endpoint = f"{_base_api_url().rstrip('/')}/api/oauth/profile"
    response = await _maybe_await(
        http_get(
            endpoint,
            headers={"Authorization": f"Bearer {accessToken}", "Content-Type": "application/json"},
            timeout=10,
        )
    )
    return await _json_response(response)


__all__ = ["getOauthProfileFromApiKey", "getOauthProfileFromOauthToken"]
