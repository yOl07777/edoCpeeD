from __future__ import annotations

from typing import Any

CHALK_BOOSTED_FOR_XTERMJS = {"provider": "deepseek", "level": 3}
CHALK_CLAMPED_FOR_TMUX = {"provider": "deepseek", "level": 2}

FG = {
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
    "gray": 90,
    "grey": 90,
}


async def applyColor(*args: Any, **kwargs: Any) -> Any:
    text = str(args[0] if args else kwargs.get("text", ""))
    color = str(args[1] if len(args) > 1 else kwargs.get("color", ""))
    code = FG.get(color)
    return text if code is None else f"\x1b[{code}m{text}\x1b[39m"


async def applyTextStyles(*args: Any, **kwargs: Any) -> Any:
    text = str(args[0] if args else kwargs.get("text", ""))
    style = args[1] if len(args) > 1 else kwargs.get("style", {})
    if not isinstance(style, dict):
        style = {}
    codes: list[str] = []
    if style.get("bold"):
        codes.append("1")
    if style.get("dim"):
        codes.append("2")
    if style.get("italic"):
        codes.append("3")
    if style.get("underline") and style.get("underline") != "none":
        codes.append("4")
    if style.get("inverse"):
        codes.append("7")
    if style.get("strikethrough"):
        codes.append("9")
    if isinstance(style.get("fg"), dict) and style["fg"].get("type") == "named":
        code = FG.get(style["fg"].get("name"))
        if code:
            codes.append(str(code))
    return text if not codes else f"\x1b[{';'.join(codes)}m{text}\x1b[0m"


async def _colorize(text: str, **style: Any) -> str:
    return await applyTextStyles(text, style)


colorize = _colorize
