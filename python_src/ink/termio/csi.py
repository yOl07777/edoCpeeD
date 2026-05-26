from __future__ import annotations

from typing import Any

CSI: str = "\x1b["
CSI_PREFIX: str = CSI
CSI_RANGE: tuple[int, int] = (0x40, 0x7E)
CURSOR_HOME: str = "\x1b[H"
CURSOR_LEFT: str = "\x1b[D"
CURSOR_RESTORE: str = "\x1b8"
CURSOR_SAVE: str = "\x1b7"
CURSOR_STYLES: dict[str, str] = {"block": "1", "underline": "3", "bar": "5"}
DISABLE_KITTY_KEYBOARD: str = "\x1b[<u"
DISABLE_MODIFY_OTHER_KEYS: str = "\x1b[>4;0m"
ENABLE_KITTY_KEYBOARD: str = "\x1b[>1u"
ENABLE_MODIFY_OTHER_KEYS: str = "\x1b[>4;1m"
ERASE_DISPLAY: str = "\x1b[J"
ERASE_LINE: str = "\x1b[2K"
ERASE_LINE_REGION: str = "\x1b[K"
ERASE_SCREEN: str = "\x1b[2J"
ERASE_SCROLLBACK: str = "\x1b[3J"
FOCUS_IN: str = "\x1b[I"
FOCUS_OUT: str = "\x1b[O"
PASTE_END: str = "\x1b[201~"
PASTE_START: str = "\x1b[200~"
RESET_SCROLL_REGION: str = "\x1b[r"


def _n(value: Any, default: int = 1) -> int:
    return max(1, int(value if value is not None else default))

async def csi(*args: Any, **kwargs: Any) -> Any:
    final = str(args[-1] if args else kwargs.get("final", ""))
    params = args[:-1] if args else kwargs.get("params", [])
    if isinstance(params, (str, int)):
        params = [params]
    body = ";".join(str(param) for param in params if param is not None)
    return f"{CSI}{body}{final}"

async def cursorBack(*args: Any, **kwargs: Any) -> Any:
    return f"{CSI}{_n(args[0] if args else kwargs.get('n'))}D"

async def cursorDown(*args: Any, **kwargs: Any) -> Any:
    return f"{CSI}{_n(args[0] if args else kwargs.get('n'))}B"

async def cursorForward(*args: Any, **kwargs: Any) -> Any:
    return f"{CSI}{_n(args[0] if args else kwargs.get('n'))}C"

async def cursorMove(*args: Any, **kwargs: Any) -> Any:
    x = int(args[0] if args else kwargs.get("x", 0) or 0)
    y = int(args[1] if len(args) > 1 else kwargs.get("y", 0) or 0)
    parts = []
    if y > 0:
        parts.append(await cursorDown(y))
    elif y < 0:
        parts.append(await cursorUp(abs(y)))
    if x > 0:
        parts.append(await cursorForward(x))
    elif x < 0:
        parts.append(await cursorBack(abs(x)))
    return "".join(parts)

async def cursorPosition(*args: Any, **kwargs: Any) -> Any:
    return "\x1b[6n"

async def cursorTo(*args: Any, **kwargs: Any) -> Any:
    x = int(args[0] if args else kwargs.get("x", 0) or 0) + 1
    y = int(args[1] if len(args) > 1 else kwargs.get("y", 0) or 0) + 1
    return f"{CSI}{y};{x}H"

async def cursorUp(*args: Any, **kwargs: Any) -> Any:
    return f"{CSI}{_n(args[0] if args else kwargs.get('n'))}A"

async def eraseLine(*args: Any, **kwargs: Any) -> Any:
    return ERASE_LINE

async def eraseLines(*args: Any, **kwargs: Any) -> Any:
    count = _n(args[0] if args else kwargs.get("count"))
    return "".join([ERASE_LINE + (await cursorUp(1)) for _ in range(count)])

async def eraseScreen(*args: Any, **kwargs: Any) -> Any:
    return ERASE_SCREEN

async def eraseToEndOfLine(*args: Any, **kwargs: Any) -> Any:
    return f"{CSI}K"

async def eraseToEndOfScreen(*args: Any, **kwargs: Any) -> Any:
    return f"{CSI}J"

async def eraseToStartOfLine(*args: Any, **kwargs: Any) -> Any:
    return f"{CSI}1K"

async def eraseToStartOfScreen(*args: Any, **kwargs: Any) -> Any:
    return f"{CSI}1J"

async def isCSIFinal(*args: Any, **kwargs: Any) -> Any:
    value = args[0] if args else kwargs.get("value", "")
    code = ord(value[0]) if isinstance(value, str) and value else int(value or 0)
    return 0x40 <= code <= 0x7E

async def isCSIIntermediate(*args: Any, **kwargs: Any) -> Any:
    value = args[0] if args else kwargs.get("value", "")
    code = ord(value[0]) if isinstance(value, str) and value else int(value or 0)
    return 0x20 <= code <= 0x2F

async def isCSIParam(*args: Any, **kwargs: Any) -> Any:
    value = args[0] if args else kwargs.get("value", "")
    code = ord(value[0]) if isinstance(value, str) and value else int(value or 0)
    return 0x30 <= code <= 0x3F

async def scrollDown(*args: Any, **kwargs: Any) -> Any:
    return f"{CSI}{_n(args[0] if args else kwargs.get('n'))}T"

async def scrollUp(*args: Any, **kwargs: Any) -> Any:
    return f"{CSI}{_n(args[0] if args else kwargs.get('n'))}S"

async def setScrollRegion(*args: Any, **kwargs: Any) -> Any:
    top = int(args[0] if args else kwargs.get("top", 0) or 0) + 1
    bottom = int(args[1] if len(args) > 1 else kwargs.get("bottom", top) or top)
    return f"{CSI}{top};{bottom}r"
