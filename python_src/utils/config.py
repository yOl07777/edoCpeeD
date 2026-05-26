"""Local global/project config helpers for the Python migration."""

from __future__ import annotations

import json
import os
import time
import uuid
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

CONFIG_WRITE_DISPLAY_THRESHOLD = 10
DEFAULT_GLOBAL_CONFIG: dict[str, Any] = {
    "hasCompletedOnboarding": False,
    "subscriptionNoticeCount": 0,
    "hasAvailableSubscription": False,
    "hasVisitedPasses": False,
    "passesLastSeenRemaining": None,
    "oauthAccount": None,
    "customApiKeyResponses": {"approved": []},
}
GLOBAL_CONFIG_KEYS = set(DEFAULT_GLOBAL_CONFIG.keys()) | {"userID", "firstStartTime", "remoteControlAtStartup"}
PROJECT_CONFIG_KEYS = {"trusted", "hasTrustDialogAccepted", "lastOnboardingVersion", "outputStyle"}
_GLOBAL_CONFIG_CACHE: dict[str, Any] | None = None
_GLOBAL_CONFIG_WRITE_COUNT = 0
_TRUST_CACHE: dict[str, bool] = {}


def _config_home() -> Path:
    return Path(os.getenv("DEEPCODE_CONFIG_HOME") or os.getenv("CLAUDE_CONFIG_DIR") or Path.home() / ".deepcode")


def _global_config_path() -> Path:
    return _config_home() / "config.json"


def getProjectPathForConfig(cwd: str | os.PathLike[str] | None = None) -> str:
    return str(Path(cwd or os.getcwd()).resolve() / ".deepseek_project.json")


def _read_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return dict(default or {})
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else dict(default or {})
    except Exception:
        return dict(default or {})


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


async def getGlobalConfig() -> dict[str, Any]:
    global _GLOBAL_CONFIG_CACHE
    if _GLOBAL_CONFIG_CACHE is None:
        _GLOBAL_CONFIG_CACHE = {**deepcopy(DEFAULT_GLOBAL_CONFIG), **_read_json(_global_config_path())}
    return deepcopy(_GLOBAL_CONFIG_CACHE)


async def saveGlobalConfig(update: dict[str, Any] | Callable[[dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
    global _GLOBAL_CONFIG_CACHE, _GLOBAL_CONFIG_WRITE_COUNT
    current = await getGlobalConfig()
    next_config = update(current) if callable(update) else {**current, **update}
    _GLOBAL_CONFIG_CACHE = deepcopy(next_config)
    _write_json(_global_config_path(), next_config)
    _GLOBAL_CONFIG_WRITE_COUNT += 1
    return deepcopy(next_config)


async def _setGlobalConfigCacheForTesting(value: dict[str, Any] | None = None) -> dict[str, Any]:
    global _GLOBAL_CONFIG_CACHE
    _GLOBAL_CONFIG_CACHE = deepcopy(value) if value is not None else None
    return await getGlobalConfig()


async def _getConfigForTesting() -> dict[str, Any]:
    return await getGlobalConfig()


async def getGlobalConfigWriteCount() -> int:
    return _GLOBAL_CONFIG_WRITE_COUNT


async def getCurrentProjectConfig(cwd: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    return _read_json(Path(getProjectPathForConfig(cwd)))


async def saveCurrentProjectConfig(update: dict[str, Any] | Callable[[dict[str, Any]], dict[str, Any]], cwd: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    current = await getCurrentProjectConfig(cwd)
    next_config = update(current) if callable(update) else {**current, **update}
    _write_json(Path(getProjectPathForConfig(cwd)), next_config)
    _TRUST_CACHE.pop(str(Path(cwd or os.getcwd()).resolve()), None)
    return deepcopy(next_config)


async def isGlobalConfigKey(key: str) -> bool:
    return key in GLOBAL_CONFIG_KEYS


async def isProjectConfigKey(key: str) -> bool:
    return key in PROJECT_CONFIG_KEYS


async def getOrCreateUserID() -> str:
    config = await getGlobalConfig()
    if config.get("userID"):
        return str(config["userID"])
    user_id = uuid.uuid4().hex
    await saveGlobalConfig({"userID": user_id})
    return user_id


async def recordFirstStartTime() -> float:
    config = await getGlobalConfig()
    if config.get("firstStartTime"):
        return float(config["firstStartTime"])
    now = time.time()
    await saveGlobalConfig({"firstStartTime": now})
    return now


async def checkHasTrustDialogAccepted(cwd: str | os.PathLike[str] | None = None) -> bool:
    key = str(Path(cwd or os.getcwd()).resolve())
    if key not in _TRUST_CACHE:
        project = await getCurrentProjectConfig(cwd)
        _TRUST_CACHE[key] = bool(project.get("hasTrustDialogAccepted") or project.get("trusted"))
    return _TRUST_CACHE[key]


async def resetTrustDialogAcceptedCacheForTesting() -> None:
    _TRUST_CACHE.clear()


async def isPathTrusted(path: str | os.PathLike[str]) -> bool:
    current = Path(path).resolve()
    while True:
        cfg = _read_json(current / ".deepseek_project.json")
        if cfg.get("trusted") or cfg.get("hasTrustDialogAccepted"):
            return True
        if current.parent == current:
            return False
        current = current.parent


async def getCustomApiKeyStatus() -> dict[str, Any]:
    approved = (await getGlobalConfig()).get("customApiKeyResponses", {}).get("approved", [])
    return {"approved": list(approved), "hasApproved": bool(approved)}


async def _wouldLoseAuthStateForTesting() -> bool:
    config = await getGlobalConfig()
    return bool(config.get("oauthAccount") or os.getenv("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEYS"))


async def enableConfigs(*_: Any, **__: Any) -> bool:
    return True


async def getMemoryPath() -> str:
    return str(_config_home() / "memory.md")


async def getUserClaudeRulesDir() -> str:
    return str(_config_home())


async def getManagedClaudeRulesDir() -> str:
    return str(Path(os.getenv("DEEPCODE_MANAGED_CONFIG_HOME") or Path.home() / ".deepcode-managed"))


async def getRemoteControlAtStartup() -> bool:
    return bool((await getGlobalConfig()).get("remoteControlAtStartup", False))


async def getAutoUpdaterDisabledReason() -> str | None:
    return os.getenv("DEEPCODE_AUTOUPDATER_DISABLED_REASON")


async def isAutoUpdaterDisabled() -> bool:
    return os.getenv("DEEPCODE_DISABLE_AUTOUPDATER", "").lower() in {"1", "true", "yes", "on"} or bool(await getAutoUpdaterDisabledReason())


async def formatAutoUpdaterDisabledReason(reason: str | None = None) -> str:
    reason = reason if reason is not None else await getAutoUpdaterDisabledReason()
    return reason or "Auto updater is enabled"


async def shouldSkipPluginAutoupdate() -> bool:
    return os.getenv("DEEPCODE_SKIP_PLUGIN_AUTOUPDATE", "").lower() in {"1", "true", "yes", "on"}
