"""Local `/advisor` command for DeepSeek advisor model selection."""

from __future__ import annotations

from inspect import isawaitable
from typing import Any

from python_src.utils.advisor import canUserConfigureAdvisor, isValidAdvisorModel, modelSupportsAdvisor
from python_src.utils.model.model import (
    getDefaultMainLoopModelSetting,
    normalizeModelStringForAPI,
    parseUserSpecifiedModel,
)
from python_src.utils.model.validateModel import validateModel
from python_src.utils.settings.settings import updateSettingsForSource


def _app_state(context: Any) -> dict[str, Any]:
    getter = getattr(context, "getAppState", None)
    if callable(getter):
        state = getter()
        return state if isinstance(state, dict) else {}
    if isinstance(context, dict):
        value = context.get("appState", context)
        return value if isinstance(value, dict) else {}
    return {}


def _set_state(context: Any, key: str, value: Any) -> None:
    setter = getattr(context, "setAppState", None)
    if callable(setter):
        setter(lambda prev: {**(prev or {}), key: value})
    elif isinstance(context, dict):
        context.setdefault("appState", {})[key] = value


async def _persist_advisor_model(value: str | None, context: Any) -> None:
    cwd = None
    if isinstance(context, dict):
        cwd = context.get("cwd") or context.get("appState", {}).get("cwd")
    try:
        result = updateSettingsForSource("user", {"advisorModel": value}, cwd=cwd)
        if isawaitable(result):
            await result
    except OSError:
        return


async def call(args: str | None = "", context: Any = None, *_unused: Any, **_kwargs: Any) -> dict[str, str]:
    arg = (args or "").strip().lower()
    state = _app_state(context)
    configured_base = state.get("mainLoopModel") or state.get("mainLoopModelOverride")
    base_model = await parseUserSpecifiedModel(configured_base or await getDefaultMainLoopModelSetting())

    if not arg:
        current = state.get("advisorModel")
        if not current:
            return {
                "type": "text",
                "value": 'Advisor: not set\nUse "/advisor <model>" to enable (e.g. "/advisor deepseek-reasoner").',
            }
        if not modelSupportsAdvisor(base_model):
            return {
                "type": "text",
                "value": f"Advisor: {current} (inactive)\nThe current model ({base_model}) does not support advisors.",
            }
        return {
            "type": "text",
            "value": f'Advisor: {current}\nUse "/advisor unset" to disable or "/advisor <model>" to change.',
        }

    if arg in {"unset", "off"}:
        previous = state.get("advisorModel")
        _set_state(context, "advisorModel", None)
        await _persist_advisor_model(None, context)
        return {"type": "text", "value": f"Advisor disabled (was {previous})." if previous else "Advisor already unset."}

    normalized_model = await normalizeModelStringForAPI(arg)
    resolved_model = await parseUserSpecifiedModel(arg)
    validation = await validateModel(resolved_model)
    valid = bool(validation.get("valid", validation.get("ok", False)))
    error = validation.get("error") or validation.get("reason")
    if not valid:
        return {"type": "text", "value": f"Invalid advisor model: {error}" if error else f"Unknown model: {arg} ({resolved_model})"}
    if not isValidAdvisorModel(resolved_model):
        return {"type": "text", "value": f"The model {arg} ({resolved_model}) cannot be used as an advisor"}

    _set_state(context, "advisorModel", normalized_model)
    await _persist_advisor_model(normalized_model, context)
    if not modelSupportsAdvisor(base_model):
        return {
            "type": "text",
            "value": (
                f"Advisor set to {normalized_model}.\n"
                f"Note: Your current model ({base_model}) does not support advisors. "
                "Switch to a supported model to use the advisor."
            ),
        }
    return {"type": "text", "value": f"Advisor set to {normalized_model}."}


advisor = {
    "type": "local",
    "name": "advisor",
    "description": "Configure the advisor model",
    "argumentHint": "[<model>|off]",
    "isEnabled": canUserConfigureAdvisor,
    "isHidden": lambda: not canUserConfigureAdvisor(),
    "supportsNonInteractive": True,
    "call": call,
}

default = advisor
