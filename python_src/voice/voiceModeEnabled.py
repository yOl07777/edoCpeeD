from __future__ import annotations

import os


def _truthy(value: str | None) -> bool:
    return (value or "").lower() in {"1", "true", "yes", "on"}


def hasVoiceAuth() -> bool:
    return bool(os.getenv("DEEPSEEK_VOICE_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("DEEPSEEK_API_KEYS"))


def isVoiceGrowthBookEnabled() -> bool:
    return _truthy(os.getenv("DEEPSEEK_VOICE_EXPERIMENT")) or _truthy(os.getenv("VOICE_MODE"))


def isVoiceModeEnabled() -> bool:
    if _truthy(os.getenv("DEEPSEEK_VOICE_DISABLED")):
        return False
    return _truthy(os.getenv("DEEPSEEK_VOICE_ENABLED")) or (isVoiceGrowthBookEnabled() and hasVoiceAuth())
