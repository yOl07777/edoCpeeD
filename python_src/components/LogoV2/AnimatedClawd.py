from __future__ import annotations

from typing import Any

from python_src.components.LogoV2._shared import LOGO_TEXT, frame_glyph, frame_index, logo_payload


async def AnimatedClawd(*args: Any, **kwargs: Any) -> Any:
    frame = kwargs.get("frame", args[0] if args and not isinstance(args[0], dict) else 0)
    glyph = frame_glyph(frame)
    return logo_payload("animated_logo_mark", text=LOGO_TEXT, glyph=glyph, frame=frame_index(frame), legacyName="Clawd")


__all__ = ["AnimatedClawd"]
