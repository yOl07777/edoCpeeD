"""Local auth refresh shim for DeepSeek API-key based auth."""

from __future__ import annotations

from typing import Any, Callable

from python_src.utils.auth import (
    clearApiKeyHelperCache,
    clearOAuthTokenCache,
    getAnthropicApiKeyWithSource,
    prefetchApiKeyFromApiKeyHelperIfSafe,
)


async def refreshAuthState() -> dict[str, Any]:
    await clearOAuthTokenCache()
    await clearApiKeyHelperCache()
    helper_key = await prefetchApiKeyFromApiKeyHelperIfSafe()
    current = await getAnthropicApiKeyWithSource()
    return {
        "provider": "deepseek",
        "source": "helper" if helper_key else current.get("source"),
        "hasKey": bool(helper_key or current.get("key")),
    }


async def call(
    onDone: Callable[[str], Any] | None = None,
    context: Any | None = None,
    args: str = "",
) -> dict[str, Any]:
    state = await refreshAuthState()
    value = (
        f"DeepSeek auth cache refreshed. API key available from {state['source']}."
        if state["hasKey"]
        else "DeepSeek auth cache refreshed. No API key is currently configured."
    )
    if onDone:
        onDone(value)
    return {"type": "oauth_refresh", "value": value, "state": state}


oauth_refresh = {
    "type": "local",
    "name": "oauth-refresh",
    "description": "Refresh local DeepSeek auth caches",
    "source": "builtin",
    "isHidden": True,
    "supportsNonInteractive": True,
    "call": call,
}

default = oauth_refresh
