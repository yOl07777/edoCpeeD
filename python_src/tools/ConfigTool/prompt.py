"""Prompt text for ConfigTool."""

from __future__ import annotations

from typing import Any

from .supportedSettings import SUPPORTED_SETTINGS

DESCRIPTION = "Read or update local DeepSeek Code configuration."


async def generatePrompt(*args: Any, **kwargs: Any) -> str:
    keys = ", ".join(sorted(SUPPORTED_SETTINGS))
    return (
        f"{DESCRIPTION} Supported settings: {keys}. "
        "Use get/list for inspection and set/delete for local workspace configuration changes."
    )


__all__ = ["DESCRIPTION", "generatePrompt"]
