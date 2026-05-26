from __future__ import annotations

from typing import Any

from python_src.components.LogoV2._shared import logo_payload, notice_text, option, scalar_arg


async def VoiceModeNotice(*args: Any, **kwargs: Any) -> Any:
    enabled = bool(option(args, kwargs, "enabled", option(args, kwargs, "voice", scalar_arg(args, False))))
    fallback = "Voice mode is enabled." if enabled else "Voice mode is currently disabled."
    return logo_payload("voice_mode_notice", enabled=enabled, text=notice_text(args, kwargs, fallback))


__all__ = ["VoiceModeNotice"]
