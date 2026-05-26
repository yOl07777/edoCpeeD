from __future__ import annotations

from typing import Any

async def parseEsc(*args: Any, **kwargs: Any) -> Any:
    sequence = str(args[0] if args else kwargs.get("sequence", ""))
    if sequence == "\x1bc":
        return {"type": "reset"}
    if sequence in ("\x1b7", "\x1b[s"):
        return {"type": "cursor", "action": {"type": "save"}}
    if sequence in ("\x1b8", "\x1b[u"):
        return {"type": "cursor", "action": {"type": "restore"}}
    return {"type": "unknown", "sequence": sequence}
