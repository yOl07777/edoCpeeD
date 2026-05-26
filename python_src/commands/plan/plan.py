"""Plan mode command."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from python_src.utils.plans import getPlan, getPlanFilePath, setPlanSlug


def _get_app_state(context: dict[str, Any] | None) -> dict[str, Any]:
    if not context:
        return {"toolPermissionContext": {"mode": "default"}}
    getter = context.get("getAppState")
    if callable(getter):
        return getter()
    return context.setdefault("appState", {"toolPermissionContext": {"mode": "default"}})


def _set_app_state(context: dict[str, Any] | None, state: dict[str, Any]) -> None:
    if not context:
        return
    setter = context.get("setAppState")
    if callable(setter):
        setter(lambda _prev: state)
    else:
        context["appState"] = state


def _done(onDone: Callable[..., Any] | None, message: str, options: dict[str, Any] | None = None) -> None:
    if not onDone:
        return
    if options:
        try:
            onDone(message, options)
            return
        except TypeError:
            pass
    onDone(message)


async def call(onDone: Callable[..., Any] | None = None, context: dict[str, Any] | None = None, args: str = "") -> dict[str, Any] | None:
    app_state = _get_app_state(context)
    permission_context = app_state.setdefault("toolPermissionContext", {})
    current_mode = permission_context.get("mode", "default")
    description = args.strip()
    cwd = (context or {}).get("cwd")
    if current_mode != "plan":
        permission_context["mode"] = "plan"
        app_state["toolPermissionContext"] = permission_context
        app_state["hasExitedPlanMode"] = False
        if description and description != "open":
            await setPlanSlug(description)
        _set_app_state(context, app_state)
        if onDone:
            _done(onDone, "Enabled plan mode", {"shouldQuery": bool(description and description != "open")})
            return None
        return {"type": "plan_mode", "enabled": True, "shouldQuery": bool(description and description != "open")}

    plan_content = await getPlan(cwd)
    plan_path = await getPlanFilePath(cwd)
    if not plan_content:
        message = "Already in plan mode. No plan written yet."
        if onDone:
            _done(onDone, message)
            return None
        return {"type": "text", "value": message}
    if description.split()[0:1] == ["open"]:
        message = f"Plan file path: {plan_path}"
        if onDone:
            _done(onDone, message)
            return None
        return {"type": "open_file", "path": plan_path}
    output = f"Current Plan\n{plan_path}\n\n{plan_content}"
    if Path(plan_path).exists():
        output += '\n\nUse "/plan open" to edit this plan.'
    if onDone:
        _done(onDone, output)
        return None
    return {"type": "text", "value": output}
