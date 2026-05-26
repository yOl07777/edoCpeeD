"""DeepSeek-oriented local auth helpers."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from python_src.utils.config import getGlobalConfig, saveGlobalConfig

credentials: dict[str, Any] = {}
_API_KEY_CACHE: dict[str, Any] | None = None
_OAUTH_TOKEN_CACHE: dict[str, Any] | None = None
_AWS_CREDENTIALS_CACHE: dict[str, Any] | None = None
_GCP_CREDENTIALS_CACHE: dict[str, Any] | None = None


def _first_env_key() -> str | None:
    value = os.getenv("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEYS")
    if not value:
        return None
    return value.split(",", 1)[0].strip() or None


async def getAnthropicApiKey() -> str | None:
    return await getApiKeyFromConfigOrMacOSKeychain()


async def getAnthropicApiKeyWithSource() -> dict[str, Any]:
    env_key = _first_env_key()
    if env_key:
        return {"key": env_key, "source": "env"}
    config = await getGlobalConfig()
    key = config.get("deepseekApiKey") or config.get("apiKey")
    return {"key": key, "source": "config" if key else None}


async def getApiKeyFromConfigOrMacOSKeychain() -> str | None:
    return (await getAnthropicApiKeyWithSource()).get("key")


async def saveApiKey(apiKey: str, *, account: dict[str, Any] | None = None) -> dict[str, Any]:
    global _API_KEY_CACHE
    await saveGlobalConfig({"deepseekApiKey": apiKey, "oauthAccount": account or {"provider": "deepseek", "accountUuid": "local-api-key"}})
    _API_KEY_CACHE = {"key": apiKey, "source": "config", "expires_at": time.time() + 3600}
    return {"saved": True, "source": "config"}


async def removeApiKey() -> None:
    global _API_KEY_CACHE, _OAUTH_TOKEN_CACHE
    config = await getGlobalConfig()
    config.pop("deepseekApiKey", None)
    config.pop("apiKey", None)
    config["oauthAccount"] = None
    await saveGlobalConfig(lambda _current: config)
    _API_KEY_CACHE = None
    _OAUTH_TOKEN_CACHE = None


async def hasAnthropicApiKeyAuth() -> bool:
    return bool(await getApiKeyFromConfigOrMacOSKeychain())


async def getAuthTokenSource() -> str | None:
    return (await getAnthropicApiKeyWithSource()).get("source")


async def getAccountInformation() -> dict[str, Any] | None:
    config = await getGlobalConfig()
    account = config.get("oauthAccount")
    if isinstance(account, dict):
        return dict(account)
    key = await getApiKeyFromConfigOrMacOSKeychain()
    return {"provider": "deepseek", "type": "api_key"} if key else None


async def getOauthAccountInfo() -> dict[str, Any] | None:
    return await getAccountInformation()


async def getClaudeAIOAuthTokensAsync() -> dict[str, Any] | None:
    return dict(_OAUTH_TOKEN_CACHE) if _OAUTH_TOKEN_CACHE else None


async def getClaudeAIOAuthTokens() -> dict[str, Any] | None:
    return await getClaudeAIOAuthTokensAsync()


async def saveOAuthTokensIfNeeded(tokens: dict[str, Any] | None = None) -> dict[str, Any] | None:
    global _OAUTH_TOKEN_CACHE
    if tokens is not None:
        _OAUTH_TOKEN_CACHE = dict(tokens)
    return await getClaudeAIOAuthTokensAsync()


async def checkAndRefreshOAuthTokenIfNeeded() -> dict[str, Any] | None:
    return await getClaudeAIOAuthTokensAsync()


async def handleOAuth401Error(*_: Any, **__: Any) -> bool:
    _OAUTH_TOKEN_CACHE = None
    return False


async def clearOAuthTokenCache() -> None:
    global _OAUTH_TOKEN_CACHE
    _OAUTH_TOKEN_CACHE = None


async def calculateApiKeyHelperTTL(started_at: float | None = None, ttl_ms: int = 300000) -> int:
    if started_at is None:
        return ttl_ms
    return max(0, ttl_ms - int((time.time() - started_at) * 1000))


async def getConfiguredApiKeyHelper() -> str | None:
    config = await getGlobalConfig()
    return config.get("apiKeyHelper") or os.getenv("DEEPSEEK_API_KEY_HELPER")


async def getApiKeyFromApiKeyHelper() -> str | None:
    helper = await getConfiguredApiKeyHelper()
    if helper and Path(helper).exists():
        return Path(helper).read_text(encoding="utf-8").strip()
    return None


async def getApiKeyFromApiKeyHelperCached() -> str | None:
    global _API_KEY_CACHE
    if _API_KEY_CACHE and _API_KEY_CACHE.get("expires_at", 0) > time.time():
        return _API_KEY_CACHE.get("key")
    key = await getApiKeyFromApiKeyHelper()
    if key:
        _API_KEY_CACHE = {"key": key, "source": "helper", "expires_at": time.time() + 300}
    return key


async def clearApiKeyHelperCache() -> None:
    global _API_KEY_CACHE
    _API_KEY_CACHE = None


async def getApiKeyHelperElapsedMs(started_at: float | None = None) -> int:
    return int((time.time() - (started_at or time.time())) * 1000)


async def getOtelHeadersFromHelper() -> dict[str, str]:
    return {}


async def getRateLimitTier() -> str:
    return os.getenv("DEEPSEEK_RATE_LIMIT_TIER", "standard")


async def getSubscriptionType() -> str:
    return os.getenv("DEEPSEEK_SUBSCRIPTION_TYPE", "api")


async def getSubscriptionName() -> str:
    return os.getenv("DEEPSEEK_SUBSCRIPTION_NAME", "DeepSeek API")


async def hasOpusAccess() -> bool:
    return False


async def hasProfileScope() -> bool:
    return bool(await getAccountInformation())


async def is1PApiCustomer() -> bool:
    return True


async def isAnthropicAuthEnabled() -> bool:
    return bool(await getApiKeyFromConfigOrMacOSKeychain())


async def isClaudeAISubscriber() -> bool:
    return bool(await getApiKeyFromConfigOrMacOSKeychain())


async def isConsumerSubscriber() -> bool:
    return False


async def isEnterpriseSubscriber() -> bool:
    return False


async def isMaxSubscriber() -> bool:
    return False


async def isProSubscriber() -> bool:
    return False


async def isTeamSubscriber() -> bool:
    return False


async def isTeamPremiumSubscriber() -> bool:
    return False


async def isOverageProvisioningAllowed() -> bool:
    return False


async def isUsing3PServices() -> bool:
    return False


async def isCustomApiKeyApproved() -> bool:
    return bool(await getApiKeyFromConfigOrMacOSKeychain())


async def checkGcpCredentialsValid() -> bool:
    return bool(_GCP_CREDENTIALS_CACHE)


async def refreshGcpCredentialsIfNeeded() -> dict[str, Any] | None:
    return _GCP_CREDENTIALS_CACHE


async def clearGcpCredentialsCache() -> None:
    global _GCP_CREDENTIALS_CACHE
    _GCP_CREDENTIALS_CACHE = None


async def refreshAwsAuth() -> dict[str, Any] | None:
    return _AWS_CREDENTIALS_CACHE


async def refreshAwsCredentialsAndBedRockInfoIfSafe() -> dict[str, Any] | None:
    return _AWS_CREDENTIALS_CACHE


async def refreshAndGetAwsCredentials() -> dict[str, Any] | None:
    return _AWS_CREDENTIALS_CACHE


async def clearAwsCredentialsCache() -> None:
    global _AWS_CREDENTIALS_CACHE
    _AWS_CREDENTIALS_CACHE = None


async def prefetchApiKeyFromApiKeyHelperIfSafe() -> str | None:
    return await getApiKeyFromApiKeyHelperCached()


async def prefetchAwsCredentialsAndBedRockInfoIfSafe() -> dict[str, Any] | None:
    return _AWS_CREDENTIALS_CACHE


async def prefetchGcpCredentialsIfSafe() -> dict[str, Any] | None:
    return _GCP_CREDENTIALS_CACHE


async def refreshGcpAuth() -> dict[str, Any] | None:
    return _GCP_CREDENTIALS_CACHE


async def isAwsAuthRefreshFromProjectSettings() -> bool:
    return False


async def isAwsCredentialExportFromProjectSettings() -> bool:
    return False


async def isGcpAuthRefreshFromProjectSettings() -> bool:
    return False


async def isOtelHeadersHelperFromProjectOrLocalSettings() -> bool:
    return False


async def validateForceLoginOrg(*_: Any, **__: Any) -> dict[str, Any]:
    return {"valid": True}
