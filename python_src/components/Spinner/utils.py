from __future__ import annotations

import re
from typing import Any


async def getDefaultCharacters(*_args: Any, **_kwargs: Any) -> list[str]:
    return ["-", "\\", "|", "/"]


async def parseRGB(value: str | tuple[int, int, int] | list[int], *_args: Any, **_kwargs: Any) -> tuple[int, int, int]:
    if isinstance(value, (tuple, list)) and len(value) >= 3:
        return tuple(max(0, min(255, int(part))) for part in value[:3])  # type: ignore[return-value]
    text = str(value).strip()
    if text.startswith("#") and len(text) in {4, 7}:
        if len(text) == 4:
            return tuple(int(ch * 2, 16) for ch in text[1:])  # type: ignore[return-value]
        return int(text[1:3], 16), int(text[3:5], 16), int(text[5:7], 16)
    nums = [int(part) for part in re.findall(r"\d+", text)[:3]]
    while len(nums) < 3:
        nums.append(0)
    return tuple(max(0, min(255, part)) for part in nums[:3])  # type: ignore[return-value]


async def toRGBColor(value: Any, *_args: Any, **_kwargs: Any) -> str:
    r, g, b = await parseRGB(value)
    return f"rgb({r}, {g}, {b})"


async def interpolateColor(start: Any, end: Any, amount: float = 0.5, *_args: Any, **_kwargs: Any) -> tuple[int, int, int]:
    sr, sg, sb = await parseRGB(start)
    er, eg, eb = await parseRGB(end)
    t = max(0.0, min(1.0, float(amount)))
    return round(sr + (er - sr) * t), round(sg + (eg - sg) * t), round(sb + (eb - sb) * t)


async def hueToRgb(hue: float, *_args: Any, **_kwargs: Any) -> tuple[int, int, int]:
    h = float(hue) % 360 / 60
    c = 255
    x = round(c * (1 - abs(h % 2 - 1)))
    if h < 1:
        return c, x, 0
    if h < 2:
        return x, c, 0
    if h < 3:
        return 0, c, x
    if h < 4:
        return 0, x, c
    if h < 5:
        return x, 0, c
    return c, 0, x


__all__ = ["getDefaultCharacters", "hueToRgb", "interpolateColor", "parseRGB", "toRGBColor"]
