"""DeepSeek logout command shim."""

from __future__ import annotations

from typing import Any

from python_src.utils.auth import clearApiKeyHelperCache, clearOAuthTokenCache, removeApiKey
from python_src.utils.config import getGlobalConfig, saveGlobalConfig
from python_src.utils.plugins.loadPluginOutputStyles import clearPluginOutputStyleCache
from python_src.utils.settings.settingsCache import resetSettingsCache


async def clearAuthRelatedCaches() -> dict[str, Any]:
    await clearOAuthTokenCache()
    await clearApiKeyHelperCache()
    await resetSettingsCache()
    await clearPluginOutputStyleCache()
    return {"cleared": True}


async def performLogout(options: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    opts = {**(options or {}), **kwargs}
    await removeApiKey()
    await clearAuthRelatedCaches()
    if opts.get("clearOnboarding"):
        config = await getGlobalConfig()
        config["hasCompletedOnboarding"] = False
        config["subscriptionNoticeCount"] = 0
        config["hasAvailableSubscription"] = False
        if isinstance(config.get("customApiKeyResponses"), dict):
            config["customApiKeyResponses"]["approved"] = []
        config["oauthAccount"] = None
        await saveGlobalConfig(config)
    return {"loggedOut": True, "clearOnboarding": bool(opts.get("clearOnboarding"))}


async def call(*_: Any, **__: Any) -> dict[str, Any]:
    await performLogout({"clearOnboarding": True})
    return {"type": "text", "value": "Successfully logged out from your DeepSeek account."}
