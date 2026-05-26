"""Local GrowthBook/feature-gate shim for the Python migration."""

from __future__ import annotations

import os
from typing import Any, Callable
from urllib.parse import urlsplit

_FEATURES: dict[str, Any] = {}
_OVERRIDES: dict[str, Any] = {}
_REFRESH_CALLBACKS: list[Callable[[dict[str, Any]], Any]] = []
_PERIODIC_RUNNING = False


async def initializeGrowthBook(features: dict[str, Any] | None = None) -> dict[str, Any]:
    _FEATURES.clear()
    _FEATURES.update(features or {})
    return {"initialized": True, "feature_count": len(_FEATURES)}


def _env_key(name: str) -> str:
    return "DEEPSEEK_FEATURE_" + "".join(ch if ch.isalnum() else "_" for ch in name).upper()


def _coerce(value: Any, default: Any = None) -> Any:
    if isinstance(value, str):
        lowered = value.lower()
        if lowered in {"true", "1", "yes", "on"}:
            return True
        if lowered in {"false", "0", "no", "off"}:
            return False
    return default if value is None else value


async def getFeatureValue_CACHED_MAY_BE_STALE(name: str, default: Any = None) -> Any:
    if name in _OVERRIDES:
        return _OVERRIDES[name]
    env_value = os.getenv(_env_key(name))
    if env_value is not None:
        return _coerce(env_value, default)
    value = _FEATURES.get(name, default)
    if isinstance(value, dict) and "value" in value:
        return value["value"]
    return value


async def getFeatureValue_CACHED_WITH_REFRESH(name: str, default: Any = None) -> Any:
    return await getFeatureValue_CACHED_MAY_BE_STALE(name, default)


async def getFeatureValue_DEPRECATED(name: str, default: Any = None) -> Any:
    return await getFeatureValue_CACHED_MAY_BE_STALE(name, default)


async def checkGate_CACHED_OR_BLOCKING(name: str, default: bool = False) -> bool:
    return bool(await getFeatureValue_CACHED_MAY_BE_STALE(name, default))


async def checkStatsigFeatureGate_CACHED_MAY_BE_STALE(name: str, default: bool = False) -> bool:
    return await checkGate_CACHED_OR_BLOCKING(name, default)


async def checkSecurityRestrictionGate(name: str, default: bool = False) -> bool:
    return await checkGate_CACHED_OR_BLOCKING(name, default)


async def getDynamicConfig_CACHED_MAY_BE_STALE(name: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
    value = await getFeatureValue_CACHED_MAY_BE_STALE(name, default or {})
    return value if isinstance(value, dict) else {"value": value}


async def getDynamicConfig_BLOCKS_ON_INIT(name: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
    return await getDynamicConfig_CACHED_MAY_BE_STALE(name, default)


async def getAllGrowthBookFeatures() -> dict[str, Any]:
    return {**_FEATURES, **_OVERRIDES}


async def getGrowthBookConfigOverrides() -> dict[str, Any]:
    return dict(_OVERRIDES)


async def setGrowthBookConfigOverride(name: str, value: Any) -> dict[str, Any]:
    _OVERRIDES[name] = value
    return {"name": name, "value": value}


async def clearGrowthBookConfigOverrides() -> None:
    _OVERRIDES.clear()


async def hasGrowthBookEnvOverride(name: str) -> bool:
    return os.getenv(_env_key(name)) is not None


async def refreshGrowthBookFeatures(features: dict[str, Any] | None = None) -> dict[str, Any]:
    if features:
        _FEATURES.update(features)
    snapshot = await getAllGrowthBookFeatures()
    for callback in list(_REFRESH_CALLBACKS):
        result = callback(snapshot)
        if hasattr(result, "__await__"):
            await result
    return snapshot


async def refreshGrowthBookAfterAuthChange() -> dict[str, Any]:
    return await refreshGrowthBookFeatures()


async def onGrowthBookRefresh(callback: Callable[[dict[str, Any]], Any]) -> dict[str, Any]:
    _REFRESH_CALLBACKS.append(callback)

    async def unsubscribe() -> None:
        if callback in _REFRESH_CALLBACKS:
            _REFRESH_CALLBACKS.remove(callback)

    return {"unsubscribe": unsubscribe}


async def setupPeriodicGrowthBookRefresh(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    global _PERIODIC_RUNNING
    _PERIODIC_RUNNING = True
    return {"running": True}


async def stopPeriodicGrowthBookRefresh() -> dict[str, Any]:
    global _PERIODIC_RUNNING
    _PERIODIC_RUNNING = False
    return {"running": False}


async def resetGrowthBook() -> None:
    _FEATURES.clear()
    _OVERRIDES.clear()
    _REFRESH_CALLBACKS.clear()


async def getApiBaseUrlHost(base_url: str | None = None) -> str:
    value = base_url or os.getenv("DEEPSEEK_ENDPOINTS", "https://api.deepseek.com").split(",", 1)[0]
    return urlsplit(value).hostname or value
