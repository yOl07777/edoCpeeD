"""DeepSeek-native `/ultraplan` command shim."""

from __future__ import annotations

from typing import Any


CCR_TERMS_URL = "https://api-docs.deepseek.com/"

DEFAULT_INSTRUCTIONS = """You are DeepSeek Code running an advanced planning pass.

Create a concrete implementation plan before any code changes are made.

Expectations:
- Inspect the repository before deciding.
- Identify the user's real goal, constraints, and risky assumptions.
- Break the work into ordered steps with verification after each meaningful change.
- Call out files or modules likely to be touched.
- Prefer existing project conventions over new architecture.
- Do not execute the plan until the user approves it or explicitly asks you to continue.
- Keep the plan specific enough that another coding agent could implement it.
"""


def buildUltraplanPrompt(blurb: str, seedPlan: str | None = None) -> str:
    parts: list[str] = []
    if seedPlan:
        parts.extend(["Here is a draft plan to refine:", "", seedPlan.strip(), ""])
    parts.append(DEFAULT_INSTRUCTIONS.strip())
    if blurb and blurb.strip():
        parts.extend(["", "User request:", blurb.strip()])
    return "\n".join(parts)


def _state_get(context: Any) -> dict[str, Any]:
    if context is None:
        return {}
    getter = getattr(context, "getAppState", None)
    if callable(getter):
        state = getter()
        return state if isinstance(state, dict) else {}
    if isinstance(context, dict):
        value = context.get("appState", context)
        return value if isinstance(value, dict) else {}
    return {}


def _state_set(context: Any, updates: dict[str, Any]) -> None:
    setter = getattr(context, "setAppState", None)
    if callable(setter):
        setter(lambda prev: {**(prev or {}), **updates})
    elif isinstance(context, dict):
        context.setdefault("appState", {}).update(updates)


def _usage() -> str:
    return "\n".join(
        [
            "Usage: /ultraplan <prompt>",
            "",
            "DeepSeek Code will draft an advanced implementation plan locally.",
            "Review and approve the plan before implementation.",
            f"DeepSeek API docs: {CCR_TERMS_URL}",
        ]
    )


def _already_active_message(active: str | None = None) -> str:
    return (
        f"ultraplan: already preparing a plan. Current marker: {active}"
        if active
        else "ultraplan: already preparing a plan. Please wait or clear the current plan state."
    )


async def launchUltraplan(*args: Any, **kwargs: Any) -> str:
    opts: dict[str, Any]
    if args and isinstance(args[0], dict):
        opts = dict(args[0])
    else:
        opts = dict(kwargs)
    blurb = str(opts.get("blurb") or "").strip()
    seed_plan = opts.get("seedPlan")
    context = opts.get("context")
    get_state = opts.get("getAppState")
    set_state = opts.get("setAppState")

    if not blurb and not seed_plan:
        return _usage()

    state = get_state() if callable(get_state) else _state_get(context)
    active = state.get("ultraplanSessionUrl") or state.get("ultraplanPrompt")
    if active or state.get("ultraplanLaunching"):
        return _already_active_message(str(active) if active else None)

    prompt = buildUltraplanPrompt(blurb, str(seed_plan) if seed_plan else None)
    updates = {"ultraplanPrompt": prompt, "ultraplanLaunching": False}
    if callable(set_state):
        set_state(lambda prev: {**(prev or {}), **updates})
    else:
        _state_set(context, updates)
    return "ultraplan: DeepSeek planning prompt prepared locally. Review the generated plan before implementing."


async def stopUltraplan(*args: Any, **kwargs: Any) -> None:
    context = kwargs.get("context")
    set_state = kwargs.get("setAppState")
    if len(args) >= 3 and callable(args[2]):
        set_state = args[2]
    updates = {"ultraplanSessionUrl": None, "ultraplanPendingChoice": None, "ultraplanLaunching": None, "ultraplanPrompt": None}
    if callable(set_state):
        set_state(lambda prev: {**(prev or {}), **updates})
    else:
        _state_set(context, updates)
    return None


async def call(onDone: Any = None, context: Any = None, args: str = "") -> None:
    blurb = (args or "").strip()
    message = await launchUltraplan({"blurb": blurb, "context": context})
    if callable(onDone):
        try:
            onDone(message, {"display": "system"})
        except TypeError:
            onDone(message)
    return None


ultraplan = {
    "type": "local-jsx",
    "name": "ultraplan",
    "description": "Draft an advanced DeepSeek Code implementation plan locally",
    "argumentHint": "<prompt>",
    "isEnabled": lambda: True,
    "call": call,
}

default = ultraplan
