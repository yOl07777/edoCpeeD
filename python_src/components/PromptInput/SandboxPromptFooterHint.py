from __future__ import annotations

from typing import Any

from python_src.components.PromptInput._shared import prompt_payload


async def SandboxPromptFooterHint(*args: Any, **kwargs: Any) -> Any:
    enabled = bool(kwargs.get("enabled", args[0] if args else True))
    return prompt_payload("sandbox_prompt_footer_hint", enabled=enabled, text="Sandbox enabled" if enabled else "Sandbox disabled")


__all__ = ["SandboxPromptFooterHint"]
