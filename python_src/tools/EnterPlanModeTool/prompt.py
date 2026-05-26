"""Prompt helper for EnterPlanModeTool."""

from __future__ import annotations

from typing import Any


async def getEnterPlanModeToolPrompt(*args: Any, **kwargs: Any) -> str:
    return (
        "Use enter_plan_mode when the user wants to pause implementation and produce a concrete plan. "
        "Provide a goal and optional ordered steps with statuses."
    )


__all__ = ["getEnterPlanModeToolPrompt"]
