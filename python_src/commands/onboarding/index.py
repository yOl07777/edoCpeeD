"""Local project onboarding command shim."""

from __future__ import annotations

from typing import Any, Callable

from python_src.projectOnboardingState import (
    getSteps,
    incrementProjectOnboardingSeenCount,
    maybeMarkProjectOnboardingComplete,
    shouldShowProjectOnboarding,
)


async def getOnboardingStatus(cwd: str | None = None) -> dict[str, Any]:
    seen = incrementProjectOnboardingSeenCount()
    complete = maybeMarkProjectOnboardingComplete(cwd)
    return {
        "provider": "deepseek",
        "seenCount": seen,
        "complete": complete,
        "shouldShow": shouldShowProjectOnboarding(cwd),
        "steps": getSteps(cwd),
    }


async def call(
    onDone: Callable[[str], Any] | None = None,
    context: Any | None = None,
    args: str = "",
) -> dict[str, Any]:
    cwd = context.get("cwd") if isinstance(context, dict) else None
    status = await getOnboardingStatus(cwd)
    done = sum(1 for step in status["steps"] if step.get("complete"))
    value = f"DeepSeek project onboarding: {done}/{len(status['steps'])} step(s) complete."
    if status["complete"]:
        value += " Project onboarding is complete."
    if onDone:
        onDone(value)
    return {"type": "onboarding", "value": value, "status": status}


onboarding = {
    "type": "local",
    "name": "onboarding",
    "description": "Show local DeepSeek project onboarding status",
    "source": "builtin",
    "isHidden": True,
    "supportsNonInteractive": True,
    "call": call,
}

default = onboarding
