from __future__ import annotations

from typing import Any

BEL: str = "\x07"
C0: range = range(0x00, 0x20)
ESC: str = "\x1b"
ESC_TYPE: str = "\x1b"
SEP: str = ";"

async def isC0(*args: Any, **kwargs: Any) -> Any:
    value = args[0] if args else kwargs.get("value", "")
    code = ord(value[0]) if isinstance(value, str) and value else int(value or 0)
    return code in C0

async def isEscFinal(*args: Any, **kwargs: Any) -> Any:
    value = args[0] if args else kwargs.get("value", "")
    code = ord(value[0]) if isinstance(value, str) and value else int(value or 0)
    return 0x30 <= code <= 0x7E
