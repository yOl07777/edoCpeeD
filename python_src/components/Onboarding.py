from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, safe_int, scalar_arg


async def Onboarding(*args: Any, **kwargs: Any) -> Any:
    steps = normalize_items(option(args, kwargs, "steps", ["Configure .env", "Run /init", "Ask DeepSeek Code to inspect the repo"]))
    current = safe_int(option(args, kwargs, "current", 0), 0)
    return component_payload("onboarding", steps=steps, current=current, complete=current >= len(steps))


async def SkippableStep(*args: Any, **kwargs: Any) -> Any:
    title = str(option(args, kwargs, "title", scalar_arg(args, "Step")))
    return component_payload("skippable_step", title=title, skipped=bool(option(args, kwargs, "skipped", False)), optional=bool(option(args, kwargs, "optional", True)))


__all__ = ["Onboarding", "SkippableStep"]
