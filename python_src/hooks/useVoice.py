from __future__ import annotations

from typing import Any

from ._basic import first_mapping, listify, normalize_bool, pick

FIRST_PRESS_FALLBACK_MS: int = 500


async def computeLevel(*args: Any, **kwargs: Any) -> Any:
    samples = [abs(float(sample)) for sample in listify(args[0] if args else kwargs.get("samples", []))]
    if not samples:
        return 0.0
    return min(1.0, sum(samples) / len(samples))

async def normalizeLanguageForSTT(*args: Any, **kwargs: Any) -> Any:
    language = str(args[0] if args else kwargs.get("language", "auto")).strip().lower()
    aliases = {"zh": "zh-CN", "cn": "zh-CN", "en": "en-US", "auto": "auto"}
    return aliases.get(language, language)

async def useVoice(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    enabled = normalize_bool(pick(options, "enabled", default=False))
    recording = enabled and normalize_bool(pick(options, "recording", default=False))
    language = await normalizeLanguageForSTT(pick(options, "language", default="auto"))
    level = await computeLevel(pick(options, "samples", default=[]))
    return {"provider": "deepseek", "enabled": enabled, "recording": recording, "language": language, "level": level}
