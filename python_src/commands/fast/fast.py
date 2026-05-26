"""Local `/fast` command."""

from __future__ import annotations

from inspect import isawaitable
from typing import Any, Awaitable, Callable

from python_src.services.analytics.index import logEvent
from python_src.utils.fastMode import (
    FAST_MODE_MODEL_DISPLAY,
    clearFastModeCooldown,
    getFastModeModel,
    getFastModeUnavailableReason,
    isFastModeEnabled,
    isFastModeSupportedByModel,
    prefetchFastModeStatus,
)
from python_src.utils.settings.settings import updateSettingsForSource

DoneCallback = Callable[[Any], Any | Awaitable[Any]]


class FastModePicker(dict):
    """Serializable stand-in for the original React picker."""

    def __init__(self, unavailableReason: str | None = None) -> None:
        super().__init__(
            type="fast_mode_picker",
            title="Fast mode",
            model=FAST_MODE_MODEL_DISPLAY,
            unavailableReason=unavailableReason,
        )


def _get_app_state(context: Any) -> dict[str, Any]:
    getter = getattr(context, "getAppState", None)
    if callable(getter):
        value = getter()
        return value if isinstance(value, dict) else {}
    if isinstance(context, dict):
        value = context.get("appState", context)
        return value if isinstance(value, dict) else {}
    return {}


def _set_app_state(context: Any, updates: dict[str, Any]) -> None:
    setter = getattr(context, "setAppState", None)
    if callable(setter):
        setter(lambda prev: {**(prev or {}), **updates})
    elif isinstance(context, dict):
        context.setdefault("appState", {}).update(updates)


async def _notify(onDone: DoneCallback | None, payload: Any) -> None:
    if onDone is None:
        return
    result = onDone(payload)
    if isawaitable(result):
        await result


async def _persist(enable: bool, context: Any) -> None:
    cwd = None
    if isinstance(context, dict):
        cwd = context.get("cwd") or context.get("appState", {}).get("cwd")
    try:
        result = updateSettingsForSource("user", {"fastMode": True if enable else None}, cwd=cwd)
        if isawaitable(result):
            await result
    except OSError:
        return


async def applyFastMode(enable: bool, context: Any) -> dict[str, Any]:
    clearFastModeCooldown()
    state = _get_app_state(context)
    updates: dict[str, Any] = {"fastMode": enable}
    if enable and not isFastModeSupportedByModel(state.get("mainLoopModel")):
        updates["mainLoopModel"] = getFastModeModel()
        updates["mainLoopModelForSession"] = None
    _set_app_state(context, updates)
    await _persist(enable, context)
    return updates


async def handleFastModeShortcut(enable: bool, context: Any) -> str:
    unavailable_reason = getFastModeUnavailableReason()
    if unavailable_reason:
        return f"Fast mode unavailable: {unavailable_reason}"
    state = _get_app_state(context)
    updates = await applyFastMode(enable, context)
    await logEvent("deepseek_fast_mode_toggled", {"enabled": enable, "source": "shortcut"})
    if enable:
        model_updated = f" - model set to {FAST_MODE_MODEL_DISPLAY}" if "mainLoopModel" in updates else ""
        return f"Fast mode ON{model_updated}"
    return "Fast mode OFF"


async def call(
    onDone: DoneCallback | None = None,
    context: Any = None,
    args: str | None = None,
) -> FastModePicker | None:
    if not isFastModeEnabled():
        return None
    await prefetchFastModeStatus()
    arg = (args or "").strip().lower()
    if arg in {"on", "off"}:
        result = await handleFastModeShortcut(arg == "on", context)
        await _notify(onDone, result)
        return None
    unavailable_reason = getFastModeUnavailableReason()
    await logEvent("deepseek_fast_mode_picker_shown", {"unavailable_reason": unavailable_reason or ""})
    return FastModePicker(unavailable_reason)
