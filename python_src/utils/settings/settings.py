from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any

from python_src.utils.settings.settingsCache import (
    getCachedSettingsForSource,
    resetSettingsCache,
    setCachedSettingsForSource,
)
from python_src.utils.settings.validation import validateSettingsFileContent


SOURCE_FILENAMES = {
    "project": ".deepseek_settings.json",
    "local": ".deepseek.local.json",
    "user": ".deepseek_user_settings.json",
    "managed": ".deepseek_managed_settings.json",
}
MERGE_ORDER = ["managed", "user", "project", "local"]


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        elif isinstance(value, list) and isinstance(result.get(key), list):
            result[key] = result[key] + value
        else:
            result[key] = deepcopy(value)
    return result


async def settingsMergeCustomizer(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    return _deep_merge(base, overlay)


async def getSettingsRootPathForSource(source: str = "project", cwd: str | os.PathLike[str] | None = None) -> str:
    if source == "user":
        return str(Path.home())
    return str(Path(cwd or os.getcwd()).resolve())


async def getRelativeSettingsFilePathForSource(source: str = "project") -> str:
    return SOURCE_FILENAMES.get(source, f".deepseek_{source}_settings.json")


async def getSettingsFilePathForSource(source: str = "project", cwd: str | os.PathLike[str] | None = None) -> str:
    return str(Path(await getSettingsRootPathForSource(source, cwd)) / await getRelativeSettingsFilePathForSource(source))


async def parseSettingsFile(path: str | os.PathLike[str]) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        return {"settings": {}, "errors": [], "path": str(file_path)}
    content = file_path.read_text(encoding="utf-8", errors="replace")
    validation = await validateSettingsFileContent(content)
    return {"settings": validation["settings"], "errors": validation["errors"], "path": str(file_path)}


async def getSettingsForSource(source: str = "project", cwd: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    cache_key = f"{source}:{Path(cwd or os.getcwd()).resolve()}"
    cached = await getCachedSettingsForSource(cache_key)
    if cached is not None:
        return cached
    path = await getSettingsFilePathForSource(source, cwd)
    parsed = await parseSettingsFile(path)
    parsed["source"] = source
    await setCachedSettingsForSource(cache_key, parsed)
    return parsed


async def getSettingsWithSources(cwd: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    sources = []
    errors = []
    for source in MERGE_ORDER:
        parsed = await getSettingsForSource(source, cwd)
        sources.append(parsed)
        errors.extend(parsed.get("errors", []))
        merged = await settingsMergeCustomizer(merged, parsed.get("settings", {}))
    env_model = os.getenv("DEFAULT_MODEL")
    if env_model:
        merged["model"] = env_model
    return {"settings": merged, "sources": sources, "errors": errors}


async def getSettingsWithErrors(cwd: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    return await getSettingsWithSources(cwd)


async def getInitialSettings(cwd: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    return (await getSettingsWithSources(cwd))["settings"]


getSettings_DEPRECATED = getInitialSettings


async def updateSettingsForSource(
    source: str,
    updates: dict[str, Any],
    *,
    cwd: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    path = Path(await getSettingsFilePathForSource(source, cwd))
    parsed = await parseSettingsFile(path)
    settings = await settingsMergeCustomizer(parsed["settings"], updates)
    path.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
    await resetSettingsCache()
    return {"path": str(path), "settings": settings}


async def rawSettingsContainsKey(raw: str | dict[str, Any], key: str) -> bool:
    if isinstance(raw, str):
        validation = await validateSettingsFileContent(raw)
        data = validation["settings"]
    else:
        data = raw
    return key in data


async def loadManagedFileSettings(cwd: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    return await getSettingsForSource("managed", cwd)


async def getManagedFileSettingsPresence(cwd: str | os.PathLike[str] | None = None) -> dict[str, bool]:
    path = Path(await getSettingsFilePathForSource("managed", cwd))
    return {"present": path.exists(), "path": str(path)}


async def getManagedSettingsKeysForLogging(cwd: str | os.PathLike[str] | None = None) -> list[str]:
    return sorted((await loadManagedFileSettings(cwd)).get("settings", {}).keys())


async def getPolicySettingsOrigin(cwd: str | os.PathLike[str] | None = None) -> str | None:
    presence = await getManagedFileSettingsPresence(cwd)
    return presence["path"] if presence["present"] else None


async def getAutoModeConfig(cwd: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    settings = await getInitialSettings(cwd)
    value = settings.get("autoMode", {})
    return value if isinstance(value, dict) else {"enabled": bool(value)}


async def hasAutoModeOptIn(cwd: str | os.PathLike[str] | None = None) -> bool:
    config = await getAutoModeConfig(cwd)
    return bool(config.get("enabled") or config.get("optIn"))


async def getUseAutoModeDuringPlan(cwd: str | os.PathLike[str] | None = None) -> bool:
    return bool((await getAutoModeConfig(cwd)).get("duringPlan", False))


async def hasSkipDangerousModePermissionPrompt(cwd: str | os.PathLike[str] | None = None) -> bool:
    settings = await getInitialSettings(cwd)
    return bool(settings.get("skipDangerousModePermissionPrompt", False))
