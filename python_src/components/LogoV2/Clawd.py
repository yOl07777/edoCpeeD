from __future__ import annotations

from typing import Any

from python_src.components.LogoV2._shared import LOGO_TEXT, logo_payload


async def Clawd(*args: Any, **kwargs: Any) -> Any:
    compact = bool(kwargs.get("compact", False))
    return logo_payload("deepseek_logo_mark", text=LOGO_TEXT, compact=compact, legacyName="Clawd")


__all__ = ["Clawd"]
