from __future__ import annotations

from typing import Any

from python_src.components.LogoV2._shared import LOGO_TEXT, frame_glyph, logo_payload, normalize_feed_items, option, scalar_arg


async def LogoV2(*args: Any, **kwargs: Any) -> Any:
    frame = option(args, kwargs, "frame", 0)
    compact = bool(option(args, kwargs, "compact", False))
    feed = normalize_feed_items(option(args, kwargs, "feed", option(args, kwargs, "items", scalar_arg(args))))
    return logo_payload(
        "logo_v2",
        text=LOGO_TEXT,
        compact=compact,
        glyph=frame_glyph(frame),
        feed=feed,
        welcome=not compact,
    )


__all__ = ["LogoV2"]
