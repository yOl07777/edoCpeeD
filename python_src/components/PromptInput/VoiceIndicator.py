from __future__ import annotations

from typing import Any

from python_src.components.PromptInput._shared import prompt_payload


async def VoiceIndicator(*args: Any, **kwargs: Any) -> Any:
    active = bool(kwargs.get("active", args[0] if args else False))
    return prompt_payload("voice_indicator", active=active, status="listening" if active else "idle")


async def VoiceWarmupHint(*args: Any, **kwargs: Any) -> Any:
    active = bool(kwargs.get("active", args[0] if args else False))
    return prompt_payload("voice_warmup_hint", active=active, text="Voice mode warming up" if active else "")


__all__ = ["VoiceIndicator", "VoiceWarmupHint"]
