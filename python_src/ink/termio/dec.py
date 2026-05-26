from __future__ import annotations

from typing import Any

DEC: dict[str, int] = {
    "CURSOR_VISIBLE": 25,
    "ALT_SCREEN": 47,
    "ALT_SCREEN_CLEAR": 1049,
    "MOUSE_NORMAL": 1000,
    "MOUSE_BUTTON": 1002,
    "MOUSE_ANY": 1003,
    "MOUSE_SGR": 1006,
    "FOCUS_EVENTS": 1004,
    "BRACKETED_PASTE": 2004,
    "SYNCHRONIZED_UPDATE": 2026,
}


def _decset(mode: int) -> str:
    return f"\x1b[?{mode}h"


def _decreset(mode: int) -> str:
    return f"\x1b[?{mode}l"


BSU: str = _decset(DEC["SYNCHRONIZED_UPDATE"])
ESU: str = _decreset(DEC["SYNCHRONIZED_UPDATE"])
EBP: str = _decset(DEC["BRACKETED_PASTE"])
DBP: str = _decreset(DEC["BRACKETED_PASTE"])
EFE: str = _decset(DEC["FOCUS_EVENTS"])
DFE: str = _decreset(DEC["FOCUS_EVENTS"])
SHOW_CURSOR: str = _decset(DEC["CURSOR_VISIBLE"])
HIDE_CURSOR: str = _decreset(DEC["CURSOR_VISIBLE"])
ENTER_ALT_SCREEN: str = _decset(DEC["ALT_SCREEN_CLEAR"])
EXIT_ALT_SCREEN: str = _decreset(DEC["ALT_SCREEN_CLEAR"])
ENABLE_MOUSE_TRACKING: str = (
    _decset(DEC["MOUSE_NORMAL"])
    + _decset(DEC["MOUSE_BUTTON"])
    + _decset(DEC["MOUSE_ANY"])
    + _decset(DEC["MOUSE_SGR"])
)
DISABLE_MOUSE_TRACKING: str = (
    _decreset(DEC["MOUSE_SGR"])
    + _decreset(DEC["MOUSE_ANY"])
    + _decreset(DEC["MOUSE_BUTTON"])
    + _decreset(DEC["MOUSE_NORMAL"])
)

async def decreset(*args: Any, **kwargs: Any) -> Any:
    mode = args[0] if args else kwargs.get("mode", 0)
    return _decreset(int(mode))

async def decset(*args: Any, **kwargs: Any) -> Any:
    mode = args[0] if args else kwargs.get("mode", 0)
    return _decset(int(mode))
