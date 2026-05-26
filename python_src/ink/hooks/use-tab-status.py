from __future__ import annotations

from typing import Any

from ..termio.osc import tabStatus


async def useTabStatus(*args: Any, **kwargs: Any) -> Any:
    status = str(args[0] if args else kwargs.get("status", ""))
    return {"provider": "deepseek", "status": status, "sequence": await tabStatus(status)}
