from __future__ import annotations

from typing import Any

async def colorsEqual(*args: Any, **kwargs: Any) -> Any:
    a = args[0] if args else kwargs.get("a", {})
    b = args[1] if len(args) > 1 else kwargs.get("b", {})
    if not isinstance(a, dict) or not isinstance(b, dict):
        return a == b
    if a.get("type") != b.get("type"):
        return False
    match a.get("type"):
        case "named":
            return a.get("name") == b.get("name")
        case "indexed":
            return a.get("index") == b.get("index")
        case "rgb":
            return all(a.get(key) == b.get(key) for key in ("r", "g", "b"))
        case "default":
            return True
    return a == b

async def defaultStyle(*args: Any, **kwargs: Any) -> Any:
    return {
        "bold": False,
        "dim": False,
        "italic": False,
        "underline": "none",
        "blink": False,
        "inverse": False,
        "hidden": False,
        "strikethrough": False,
        "overline": False,
        "fg": {"type": "default"},
        "bg": {"type": "default"},
        "underlineColor": {"type": "default"},
    }

async def stylesEqual(*args: Any, **kwargs: Any) -> Any:
    a = args[0] if args else kwargs.get("a", {})
    b = args[1] if len(args) > 1 else kwargs.get("b", {})
    keys = ("bold", "dim", "italic", "underline", "blink", "inverse", "hidden", "strikethrough", "overline")
    if any(a.get(key) != b.get(key) for key in keys):
        return False
    return (
        await colorsEqual(a.get("fg"), b.get("fg"))
        and await colorsEqual(a.get("bg"), b.get("bg"))
        and await colorsEqual(a.get("underlineColor"), b.get("underlineColor"))
    )
