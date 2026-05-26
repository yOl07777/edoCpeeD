"""FileReadTool limit helpers."""

from __future__ import annotations

from typing import Any

DEFAULT_MAX_OUTPUT_TOKENS = 20_000


async def getDefaultFileReadingLimits(*args: Any, **kwargs: Any) -> dict[str, int]:
    max_tokens = int(kwargs.get("maxOutputTokens") or kwargs.get("max_output_tokens") or DEFAULT_MAX_OUTPUT_TOKENS)
    chars_per_token = int(kwargs.get("charsPerToken") or kwargs.get("chars_per_token") or 4)
    return {
        "max_output_tokens": max_tokens,
        "max_chars": max_tokens * chars_per_token,
        "max_lines": int(kwargs.get("maxLines") or kwargs.get("max_lines") or 2_000),
    }


__all__ = ["DEFAULT_MAX_OUTPUT_TOKENS", "getDefaultFileReadingLimits"]
