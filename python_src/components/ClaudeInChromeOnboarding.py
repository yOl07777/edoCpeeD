from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option


async def ClaudeInChromeOnboarding(*args: Any, **kwargs: Any) -> Any:
    installed = bool(option(args, kwargs, "installed", False))
    return component_payload(
        "browser_onboarding",
        legacyName="ClaudeInChromeOnboarding",
        title="DeepSeek Code browser handoff",
        installed=installed,
        action="open_instructions" if not installed else "ready",
    )


__all__ = ["ClaudeInChromeOnboarding"]
