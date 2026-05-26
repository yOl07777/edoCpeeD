"""Local policy limits service for the Python migration.

The original service polls Anthropic organization policy APIs.  DeepSeek Code's
Python migration keeps policy decisions fail-open and local: restrictions can
be injected via environment JSON or a cache file, and no network traffic is
performed.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .types import PolicyLimitsResponseSchema

CACHE_FILENAME = "policy-limits.json"

_polling = False
_loading_event: asyncio.Event | None = None
_session_cache: dict[str, dict[str, bool]] | None = None
_etag: str | None = None


def _config_home() -> Path:
    root = os.getenv("DEEPCODE_CONFIG_HOME") or os.getenv("DEEPSEEK_CODE_HOME")
    return Path(root).expanduser().resolve() if root else (Path.home() / ".deepcode").resolve()


def _cache_path() -> Path:
    return _config_home() / CACHE_FILENAME


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _checksum(restrictions: dict[str, Any]) -> str:
    raw = json.dumps(restrictions, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _env_restrictions() -> dict[str, Any] | None:
    raw = os.getenv("DEEPCODE_POLICY_LIMITS") or os.getenv("DEEPSEEK_POLICY_LIMITS")
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except Exception:
        return None
    if isinstance(data, dict) and "restrictions" in data:
        return data
    if isinstance(data, dict):
        return {"restrictions": data}
    return None


def _normalize_response(data: Any) -> dict[str, dict[str, bool]]:
    parsed = PolicyLimitsResponseSchema().safeParse(data or {"restrictions": {}})
    if not parsed.success:
        return {}
    return parsed.data["restrictions"]


def _resolve_loading() -> None:
    if _loading_event is not None:
        _loading_event.set()


async def _resetPolicyLimitsForTesting(*args: Any, **kwargs: Any) -> None:
    global _polling, _loading_event, _session_cache, _etag
    _polling = False
    _loading_event = None
    _session_cache = None
    _etag = None


async def initializePolicyLimitsLoadingPromise(*args: Any, **kwargs: Any) -> dict[str, Any]:
    global _loading_event
    if _loading_event is None:
        _loading_event = asyncio.Event()
        if not await isPolicyLimitsEligible():
            _loading_event.set()
    return {"initialized": True, "eligible": await isPolicyLimitsEligible()}


async def waitForPolicyLimitsToLoad(*args: Any, **kwargs: Any) -> None:
    if _loading_event is not None:
        timeout = float(kwargs.get("timeout") or kwargs.get("timeoutSeconds") or 30)
        try:
            await asyncio.wait_for(_loading_event.wait(), timeout)
        except asyncio.TimeoutError:
            _loading_event.set()


async def isPolicyLimitsEligible(*args: Any, **kwargs: Any) -> bool:
    value = os.getenv("DEEPCODE_POLICY_LIMITS_ELIGIBLE") or os.getenv("DEEPSEEK_POLICY_LIMITS_ELIGIBLE")
    if value is None:
        return True
    return value.lower() in {"1", "true", "yes", "on"}


async def loadPolicyLimits(*args: Any, **kwargs: Any) -> dict[str, Any]:
    global _session_cache, _etag
    if not await isPolicyLimitsEligible():
        _session_cache = {}
        _resolve_loading()
        return {"success": True, "restrictions": {}, "eligible": False, "source": "ineligible"}
    source = "env"
    data = _env_restrictions()
    if data is None:
        source = "cache"
        data = _read_json(_cache_path()) or {"restrictions": {}}
    restrictions = _normalize_response(data)
    _session_cache = restrictions
    _etag = str(data.get("etag") or _checksum(restrictions)) if isinstance(data, dict) else _checksum(restrictions)
    _resolve_loading()
    return {"success": True, "restrictions": restrictions, "etag": _etag, "source": source}


async def refreshPolicyLimits(*args: Any, **kwargs: Any) -> dict[str, Any]:
    result = await loadPolicyLimits()
    if result.get("success"):
        _write_json(_cache_path(), {"restrictions": result.get("restrictions", {}), "etag": result.get("etag")})
    return result


async def clearPolicyLimitsCache(*args: Any, **kwargs: Any) -> dict[str, Any]:
    global _session_cache, _etag
    _session_cache = None
    _etag = None
    removed = False
    try:
        _cache_path().unlink()
        removed = True
    except FileNotFoundError:
        removed = False
    except Exception:
        removed = False
    return {"cleared": True, "fileRemoved": removed, "path": str(_cache_path())}


async def isPolicyAllowed(*args: Any, **kwargs: Any) -> bool:
    policy = str(kwargs.get("policy") or kwargs.get("policyName") or (args[0] if args else ""))
    global _session_cache
    if _session_cache is None:
        await loadPolicyLimits()
    if not policy:
        return True
    restriction = (_session_cache or {}).get(policy)
    if restriction is None:
        return True
    return bool(restriction.get("allowed", True))


async def startBackgroundPolling(*args: Any, **kwargs: Any) -> dict[str, Any]:
    global _polling
    _polling = True
    await loadPolicyLimits()
    return {"started": True, "intervalMs": int(kwargs.get("intervalMs") or 60 * 60 * 1000)}


async def stopBackgroundPolling(*args: Any, **kwargs: Any) -> dict[str, Any]:
    global _polling
    was_polling = _polling
    _polling = False
    return {"stopped": was_polling}


__all__ = [
    "_resetPolicyLimitsForTesting",
    "clearPolicyLimitsCache",
    "initializePolicyLimitsLoadingPromise",
    "isPolicyAllowed",
    "isPolicyLimitsEligible",
    "loadPolicyLimits",
    "refreshPolicyLimits",
    "startBackgroundPolling",
    "stopBackgroundPolling",
    "waitForPolicyLimitsToLoad",
]
