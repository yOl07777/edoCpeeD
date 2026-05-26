"""Local `/brief` command for toggling brief-only output mode."""

from __future__ import annotations

import os
from inspect import isawaitable
from typing import Any, Awaitable, Callable

from python_src.bootstrap.state import getKairosActive, setUserMsgOptIn
from python_src.services.analytics.index import logEvent

DoneCallback = Callable[[Any], Any | Awaitable[Any]]


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def getBriefConfig() -> dict[str, bool]:
    return {"enable_slash_command": _truthy(os.getenv("DEEPSEEK_BRIEF_COMMAND_ENABLED"))}


def isEnabled() -> bool:
    return getBriefConfig()["enable_slash_command"] or _truthy(os.getenv("KAIROS")) or _truthy(os.getenv("KAIROS_BRIEF"))


def _get_app_state(context: Any) -> dict[str, Any]:
    if context is None:
        return {}
    getter = getattr(context, "getAppState", None)
    if callable(getter):
        value = getter()
        return value if isinstance(value, dict) else {}
    if isinstance(context, dict):
        app_state = context.get("appState", context)
        return app_state if isinstance(app_state, dict) else {}
    return {}


def _set_app_state(context: Any, app_state: dict[str, Any]) -> None:
    setter = getattr(context, "setAppState", None)
    if callable(setter):
        setter(lambda prev: {**(prev or {}), **app_state})
    elif isinstance(context, dict):
        context.setdefault("appState", {}).update(app_state)


async def _notify(onDone: DoneCallback | None, message: str, options: dict[str, Any]) -> None:
    if onDone is None:
        return
    result = onDone(message, options)
    if isawaitable(result):
        await result


async def call(
    onDone: DoneCallback | None = None,
    context: Any = None,
    *_args: Any,
    **_kwargs: Any,
) -> None:
    app_state = _get_app_state(context)
    new_state = not bool(app_state.get("isBriefOnly"))
    setUserMsgOptIn(new_state)
    _set_app_state(context, {"isBriefOnly": new_state})
    await logEvent(
        "deepseek_brief_mode_toggled",
        {"enabled": new_state, "gated": False, "source": "slash_command"},
    )
    meta_messages = None
    if not getKairosActive():
        meta_messages = [
            "<system-reminder>\n"
            + (
                "Brief mode is now enabled. Keep user-facing output concise."
                if new_state
                else "Brief mode is now disabled. Reply normally."
            )
            + "\n</system-reminder>"
        ]
    await _notify(
        onDone,
        "Brief-only mode enabled" if new_state else "Brief-only mode disabled",
        {"display": "system", "metaMessages": meta_messages},
    )
    return None


brief = {
    "type": "local-jsx",
    "name": "brief",
    "description": "Toggle brief-only mode",
    "isEnabled": isEnabled,
    "immediate": True,
    "call": call,
}

default = brief
