from __future__ import annotations

from typing import Any

from python_src.components.LogoV2._shared import frame_glyph, frame_index, logo_payload


async def AnimatedAsterisk(*args: Any, **kwargs: Any) -> Any:
    frame = kwargs.get("frame", args[0] if args and not isinstance(args[0], dict) else 0)
    glyph = frame_glyph(frame)
    return logo_payload("animated_asterisk", frame=frame_index(frame), glyph=glyph, text=glyph)


__all__ = ["AnimatedAsterisk"]
