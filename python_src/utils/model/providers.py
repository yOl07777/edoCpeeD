from __future__ import annotations

import os


async def getAPIProvider() -> str:
    return os.getenv("DEEPSEEK_PROVIDER", "deepseek")


async def getAPIProviderForStatsig() -> str:
    return await getAPIProvider()


async def isFirstPartyAnthropicBaseUrl(url: str | None = None) -> bool:
    # The Python migration intentionally does not treat Anthropic URLs as first-party.
    target = (url or os.getenv("DEEPSEEK_ENDPOINTS", "")).lower()
    return "api.deepseek.com" in target
