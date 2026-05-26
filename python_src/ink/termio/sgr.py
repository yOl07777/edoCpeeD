from __future__ import annotations

from typing import Any

from .types import defaultStyle


NAMED_COLORS = [
    "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
    "brightBlack", "brightRed", "brightGreen", "brightYellow", "brightBlue",
    "brightMagenta", "brightCyan", "brightWhite",
]
UNDERLINE_STYLES = ["none", "single", "double", "curly", "dotted", "dashed"]


def _parse_param(value: str) -> tuple[int | None, list[int], bool]:
    if ":" not in value:
        return (int(value) if value else None, [], False)
    pieces = value.split(":")
    head = int(pieces[0]) if pieces[0] else None
    return head, [int(piece) for piece in pieces[1:] if piece], True


def _parse_params(param_str: str) -> list[tuple[int | None, list[int], bool]]:
    if param_str == "":
        return [(0, [], False)]
    return [_parse_param(part) for part in param_str.split(";")]


def _extended_color(params: list[tuple[int | None, list[int], bool]], idx: int) -> tuple[dict[str, Any] | None, int]:
    value, subparams, colon = params[idx]
    if colon and subparams:
        if subparams[0] == 5 and len(subparams) >= 2:
            return {"type": "indexed", "index": subparams[1]}, 1
        if subparams[0] == 2 and len(subparams) >= 4:
            off = 1 if len(subparams) >= 5 else 0
            return {"type": "rgb", "r": subparams[1 + off], "g": subparams[2 + off], "b": subparams[3 + off]}, 1
    if idx + 1 >= len(params):
        return None, 1
    mode = params[idx + 1][0]
    if mode == 5 and idx + 2 < len(params) and params[idx + 2][0] is not None:
        return {"type": "indexed", "index": params[idx + 2][0]}, 3
    if mode == 2 and idx + 4 < len(params):
        rgb = [params[idx + offset][0] for offset in (2, 3, 4)]
        if all(component is not None for component in rgb):
            return {"type": "rgb", "r": rgb[0], "g": rgb[1], "b": rgb[2]}, 5
    return None, 1


async def applySGR(*args: Any, **kwargs: Any) -> Any:
    param_str = str(args[0] if args else kwargs.get("paramStr", kwargs.get("params", "")))
    style = args[1] if len(args) > 1 else kwargs.get("style")
    current = dict(style or await defaultStyle())
    params = _parse_params(param_str)
    i = 0
    while i < len(params):
        code, subparams, colon = params[i]
        code = code or 0
        if code == 0:
            current = await defaultStyle()
        elif code == 1:
            current["bold"] = True
        elif code == 2:
            current["dim"] = True
        elif code == 3:
            current["italic"] = True
        elif code == 4:
            current["underline"] = UNDERLINE_STYLES[subparams[0]] if colon and subparams and subparams[0] < len(UNDERLINE_STYLES) else "single"
        elif code in (5, 6):
            current["blink"] = True
        elif code == 7:
            current["inverse"] = True
        elif code == 8:
            current["hidden"] = True
        elif code == 9:
            current["strikethrough"] = True
        elif code == 21:
            current["underline"] = "double"
        elif code == 22:
            current["bold"] = False
            current["dim"] = False
        elif code == 23:
            current["italic"] = False
        elif code == 24:
            current["underline"] = "none"
        elif code == 25:
            current["blink"] = False
        elif code == 27:
            current["inverse"] = False
        elif code == 28:
            current["hidden"] = False
        elif code == 29:
            current["strikethrough"] = False
        elif code == 53:
            current["overline"] = True
        elif code == 55:
            current["overline"] = False
        elif 30 <= code <= 37:
            current["fg"] = {"type": "named", "name": NAMED_COLORS[code - 30]}
        elif code == 39:
            current["fg"] = {"type": "default"}
        elif 40 <= code <= 47:
            current["bg"] = {"type": "named", "name": NAMED_COLORS[code - 40]}
        elif code == 49:
            current["bg"] = {"type": "default"}
        elif 90 <= code <= 97:
            current["fg"] = {"type": "named", "name": NAMED_COLORS[code - 90 + 8]}
        elif 100 <= code <= 107:
            current["bg"] = {"type": "named", "name": NAMED_COLORS[code - 100 + 8]}
        elif code in (38, 48, 58):
            color, step = _extended_color(params, i)
            if color:
                current["fg" if code == 38 else "bg" if code == 48 else "underlineColor"] = color
                i += step
                continue
        elif code == 59:
            current["underlineColor"] = {"type": "default"}
        i += 1
    return current
