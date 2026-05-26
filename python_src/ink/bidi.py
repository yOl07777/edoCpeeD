from __future__ import annotations

from typing import Any


async def reorderBidi(*args: Any, **kwargs: Any) -> Any:
    text = str(args[0] if args else kwargs.get("text", ""))
    return text
