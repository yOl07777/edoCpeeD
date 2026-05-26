from __future__ import annotations

from typing import Any

from python_src.components.Spinner.SpinnerGlyph import SpinnerGlyph


async def SpinnerAnimationRow(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    glyph = await SpinnerGlyph(frame=kwargs.get("frame", 0))
    message = kwargs.get("message") or "Working"
    return {"type": "spinner_animation_row", "provider": "deepseek", "text": f"{glyph['glyph']} {message}"}


__all__ = ["SpinnerAnimationRow"]
