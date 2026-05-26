"""Fast mode state helpers for the DeepSeek migration."""

from __future__ import annotations

import os
import time
from typing import Any, Callable

from deepseek_code.config import DeepSeekConfig
from python_src.utils.model.aliases import resolve_model_alias

FAST_MODE_MODEL_DISPLAY = "deepseek-chat"

onCooldownExpired: Callable[[dict[str, Any]], Any] | None = None
onCooldownTriggered: Callable[[dict[str, Any]], Any] | None = None
onFastModeOverageRejection: Callable[[dict[str, Any]], Any] | None = None
onOrgFastModeChanged: Callable[[dict[str, Any]], Any] | None = None

_RUNTIME_STATE: dict[str, Any] = {"status": "available", "reason": None, "resetAt": None}
_ORG_ENABLED = True


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _notify(callback: Callable[[dict[str, Any]], Any] | None, payload: dict[str, Any]) -> None:
    if callback is not None:
        callback(payload)


def getFastModeModel() -> str:
    return os.getenv("DEEPSEEK_FAST_MODE_MODEL") or "deepseek-chat"


def getFastModeRuntimeState() -> dict[str, Any]:
    if _RUNTIME_STATE.get("status") == "cooldown":
        reset_at = _RUNTIME_STATE.get("resetAt")
        if reset_at is not None and float(reset_at) <= time.time() * 1000:
            clearFastModeCooldown()
    return dict(_RUNTIME_STATE)


def getFastModeState() -> dict[str, Any]:
    return {"enabled": isFastModeEnabled(), "runtime": getFastModeRuntimeState(), "model": getFastModeModel()}


def clearFastModeCooldown() -> dict[str, Any]:
    _RUNTIME_STATE.update({"status": "available", "reason": None, "resetAt": None})
    _notify(onCooldownExpired, dict(_RUNTIME_STATE))
    return dict(_RUNTIME_STATE)


def triggerFastModeCooldown(reason: str = "rate_limit", resetAt: int | float | None = None, resetInMs: int | None = None) -> dict[str, Any]:
    reset_at = resetAt if resetAt is not None else time.time() * 1000 + int(resetInMs or 60_000)
    _RUNTIME_STATE.update({"status": "cooldown", "reason": reason, "resetAt": reset_at})
    _notify(onCooldownTriggered, dict(_RUNTIME_STATE))
    return dict(_RUNTIME_STATE)


def handleFastModeOverageRejection(reason: str = "overage", resetInMs: int | None = None) -> dict[str, Any]:
    state = triggerFastModeCooldown(reason, resetInMs=resetInMs)
    _notify(onFastModeOverageRejection, state)
    return state


def handleFastModeRejectedByAPI(error: Any = None) -> dict[str, Any]:
    text = str(error or "").lower()
    reason = "overloaded" if "overload" in text or "503" in text else "rate_limit"
    return triggerFastModeCooldown(reason)


def isFastModeCooldown() -> bool:
    return getFastModeRuntimeState().get("status") == "cooldown"


def isFastModeAvailable() -> bool:
    return _ORG_ENABLED and not isFastModeCooldown()


def getFastModeUnavailableReason() -> str | None:
    if not _ORG_ENABLED:
        return "Fast mode is disabled for this environment."
    state = getFastModeRuntimeState()
    if state.get("status") == "cooldown":
        return "Fast mode is temporarily unavailable."
    return None


def isFastModeEnabled() -> bool:
    if os.getenv("DEEPSEEK_FAST_MODE_ENABLED") is not None:
        return _truthy(os.getenv("DEEPSEEK_FAST_MODE_ENABLED"))
    return getFastModeModel() in set(DeepSeekConfig.from_env().models) | {"deepseek-chat", "deepseek-coder", "deepseek-reasoner"}


def isFastModeSupportedByModel(model: str | None) -> bool:
    canonical = resolve_model_alias(model or "").lower()
    return canonical == getFastModeModel().lower()


def getInitialFastModeSetting(settings: dict[str, Any] | None = None) -> bool:
    if os.getenv("DEEPSEEK_FAST_MODE_DEFAULT") is not None:
        return _truthy(os.getenv("DEEPSEEK_FAST_MODE_DEFAULT"))
    return bool((settings or {}).get("fastMode", False))


def resolveFastModeStatusFromCache(status: dict[str, Any] | None = None) -> dict[str, Any]:
    global _ORG_ENABLED
    if status and "enabled" in status:
        _ORG_ENABLED = bool(status["enabled"])
        _notify(onOrgFastModeChanged, {"enabled": _ORG_ENABLED})
    return {"enabled": _ORG_ENABLED, "runtime": getFastModeRuntimeState()}


async def prefetchFastModeStatus(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    return resolveFastModeStatusFromCache()
