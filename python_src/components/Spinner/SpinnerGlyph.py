from __future__ import annotations

from typing import Any

from python_src.components.Spinner.utils import getDefaultCharacters


async def SpinnerGlyph(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    chars = kwargs.get("characters") or await getDefaultCharacters()
    frame = int(kwargs.get("frame", 0) or 0)
    glyph = chars[frame % len(chars)] if chars else "-"
    return {"type": "spinner_glyph", "provider": "deepseek", "glyph": glyph, "frame": frame}


__all__ = ["SpinnerGlyph"]
