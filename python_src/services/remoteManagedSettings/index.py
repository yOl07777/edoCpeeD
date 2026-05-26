"""Local remote-managed-settings service for the Python migration."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .securityCheck import checkManagedSettingsSecurity, handleSecurityCheckResult
from .syncCache import isRemoteManagedSettingsEligible
from .syncCacheState import getSettingsPath, setEligibility, setSessionCache
from .types import RemoteManagedSettingsResponseSchema

_polling = False
_loading_event: asyncio.Event | None = None
_session_cache: dict[str, Any] | None = None
_checksum: str | None = None


def _config_home() -> Path:
    root = os.getenv("DEEPCODE_CONFIG_HOME") or os.getenv("DEEPSEEK_CODE_HOME")
    return Path(root).expanduser().resolve() if root else (Path.home() / ".deepcode").resolve()


def _cache_path() -> Path:
    return _config_home() / "remote-settings.json"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


async def computeChecksumFromSettings(*args: Any, **kwargs: Any) -> str:
    settings = kwargs.get("settings") if "settings" in kwargs else (args[0] if args else {})
    raw = json.dumps(settings or {}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _env_response() -> dict[str, Any] | None:
    raw = os.getenv("DEEPCODE_REMOTE_MANAGED_SETTINGS") or os.getenv("DEEPSEEK_REMOTE_MANAGED_SETTINGS")
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except Exception:
        return None
    if isinstance(data, dict) and "settings" in data:
        return data
    if isinstance(data, dict):
        return {"uuid": "env", "checksum": "", "settings": data}
    return None


def _resolve_loading() -> None:
    if _loading_event is not None:
        _loading_event.set()


async def initializeRemoteManagedSettingsLoadingPromise(*args: Any, **kwargs: Any) -> dict[str, Any]:
    global _loading_event
    if _loading_event is None:
        _loading_event = asyncio.Event()
        if not await isEligibleForRemoteManagedSettings():
            _loading_event.set()
    return {"initialized": True, "eligible": await isEligibleForRemoteManagedSettings()}


async def waitForRemoteManagedSettingsToLoad(*args: Any, **kwargs: Any) -> None:
    if _loading_event is not None:
        timeout = float(kwargs.get("timeout") or kwargs.get("timeoutSeconds") or 30)
        try:
            await asyncio.wait_for(_loading_event.wait(), timeout)
        except asyncio.TimeoutError:
            _loading_event.set()


async def isEligibleForRemoteManagedSettings(*args: Any, **kwargs: Any) -> bool:
    return await isRemoteManagedSettingsEligible()


async def loadRemoteManagedSettings(*args: Any, **kwargs: Any) -> dict[str, Any]:
    global _session_cache, _checksum
    eligible = await isEligibleForRemoteManagedSettings()
    await setEligibility(eligible)
    if not eligible:
        _session_cache = None
        _resolve_loading()
        return {"success": True, "settings": {}, "eligible": False, "source": "ineligible"}

    source = "env"
    response = _env_response()
    if response is None:
        source = "cache"
        cached = _read_json(_cache_path()) or {}
        response = {"uuid": cached.get("uuid", "cache"), "checksum": cached.get("checksum", ""), "settings": cached}
    parsed = RemoteManagedSettingsResponseSchema().safeParse(response)
    if not parsed.success:
        _session_cache = {}
        _resolve_loading()
        return {"success": False, "settings": {}, "error": parsed.error.issues[0].message if parsed.error else "invalid settings"}

    settings = parsed.data["settings"]
    cached_settings = _session_cache or _read_json(_cache_path())
    security = await checkManagedSettingsSecurity(cached_settings, settings)
    if not await handleSecurityCheckResult(security):
        return {"success": False, "settings": {}, "error": "managed settings rejected", "securityCheck": security}

    _checksum = parsed.data["checksum"] or await computeChecksumFromSettings(settings)
    _session_cache = dict(settings)
    await setSessionCache(_session_cache)
    _resolve_loading()
    return {"success": True, "settings": dict(settings), "checksum": _checksum, "uuid": parsed.data["uuid"], "source": source, "securityCheck": security}


async def refreshRemoteManagedSettings(*args: Any, **kwargs: Any) -> dict[str, Any]:
    result = await loadRemoteManagedSettings()
    if result.get("success"):
        data = dict(result.get("settings") or {})
        data["uuid"] = result.get("uuid", "local")
        data["checksum"] = result.get("checksum")
        _write_json(_cache_path(), data)
    return result


async def clearRemoteManagedSettingsCache(*args: Any, **kwargs: Any) -> dict[str, Any]:
    global _session_cache, _checksum
    _session_cache = None
    _checksum = None
    await setSessionCache(None)
    removed = False
    try:
        _cache_path().unlink()
        removed = True
    except FileNotFoundError:
        removed = False
    except Exception:
        removed = False
    return {"cleared": True, "fileRemoved": removed, "path": await getSettingsPath()}


async def startBackgroundPolling(*args: Any, **kwargs: Any) -> dict[str, Any]:
    global _polling
    _polling = True
    await loadRemoteManagedSettings()
    return {"started": True, "intervalMs": int(kwargs.get("intervalMs") or 60 * 60 * 1000)}


async def stopBackgroundPolling(*args: Any, **kwargs: Any) -> dict[str, Any]:
    global _polling
    was_polling = _polling
    _polling = False
    return {"stopped": was_polling}


__all__ = [
    "clearRemoteManagedSettingsCache",
    "computeChecksumFromSettings",
    "initializeRemoteManagedSettingsLoadingPromise",
    "isEligibleForRemoteManagedSettings",
    "loadRemoteManagedSettings",
    "refreshRemoteManagedSettings",
    "startBackgroundPolling",
    "stopBackgroundPolling",
    "waitForRemoteManagedSettingsToLoad",
]
