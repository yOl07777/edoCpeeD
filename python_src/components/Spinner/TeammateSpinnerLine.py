from __future__ import annotations

from typing import Any


async def TeammateSpinnerLine(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    name = kwargs.get("name") or kwargs.get("agent") or "agent"
    status = kwargs.get("status") or "working"
    return {"type": "teammate_spinner_line", "provider": "deepseek", "name": str(name), "status": str(status)}


__all__ = ["TeammateSpinnerLine"]
