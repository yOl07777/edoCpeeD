"""DeepSeek login command shim."""

from __future__ import annotations

import os
from typing import Any, Callable

from python_src.bootstrap.state import resetCostState
from python_src.utils.auth import getAnthropicApiKeyWithSource, saveApiKey


async def Login(onDone: Callable[..., Any] | None = None, startingMessage: str | None = None, apiKey: str | None = None) -> dict[str, Any]:
    key = apiKey or os.getenv("DEEPSEEK_API_KEY") or (os.getenv("DEEPSEEK_API_KEYS", "").split(",", 1)[0].strip() or None)
    if key:
        await saveApiKey(key)
        if onDone:
            onDone(True, os.getenv("DEFAULT_MODEL", "deepseek-chat"))
        return {"type": "login", "success": True, "provider": "deepseek", "source": "env_or_arg"}
    return {
        "type": "login",
        "success": False,
        "provider": "deepseek",
        "message": startingMessage or "Set DEEPSEEK_API_KEY or DEEPSEEK_API_KEYS to log in.",
    }


async def call(onDone: Callable[..., Any] | None = None, context: dict[str, Any] | None = None, args: str = "") -> dict[str, Any] | None:
    api_key = args.strip() or None
    result = await Login(apiKey=api_key)
    if result["success"]:
        resetCostState()
        if context:
            if callable(context.get("onChangeAPIKey")):
                context["onChangeAPIKey"]()
            app_state = context.get("appState")
            if isinstance(app_state, dict):
                app_state["authVersion"] = int(app_state.get("authVersion", 0)) + 1
        if onDone:
            onDone("Login successful")
            return None
    else:
        if onDone:
            onDone("Login interrupted")
            return None
    return result


async def getLoginStatus() -> dict[str, Any]:
    resolved = await getAnthropicApiKeyWithSource()
    return {"loggedIn": bool(resolved.get("key")), "source": resolved.get("source"), "provider": "deepseek"}
