from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option


async def IdeOnboardingDialog(*args: Any, **kwargs: Any) -> Any:
    ide = str(option(args, kwargs, "ide", "VS Code"))
    steps = normalize_items(option(args, kwargs, "steps", ["Install DeepSeek Code extension", "Open this workspace", "Enable terminal handoff"]))
    return component_payload("ide_onboarding_dialog", ide=ide, shown=not await hasIdeOnboardingDialogBeenShown(*args, **kwargs), steps=steps)


async def hasIdeOnboardingDialogBeenShown(*args: Any, **kwargs: Any) -> Any:
    return bool(option(args, kwargs, "shown", option(args, kwargs, "hasShown", False)))


__all__ = ["IdeOnboardingDialog", "hasIdeOnboardingDialogBeenShown"]
