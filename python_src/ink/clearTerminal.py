from __future__ import annotations

from typing import Any


async def clearTerminal(*args: Any, **kwargs: Any) -> Any:
    include_scrollback = bool(kwargs.get("scrollback", kwargs.get("includeScrollback", False)))
    return "\x1b[3J\x1b[2J\x1b[H" if include_scrollback else "\x1b[2J\x1b[H"
