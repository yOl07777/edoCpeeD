from __future__ import annotations

from typing import Any


_IDE_LOGS: list[dict[str, Any]] = []


async def useIdeLogging(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    if kwargs.get("clear"):
        _IDE_LOGS.clear()
    if "message" in kwargs:
        _IDE_LOGS.append({"level": kwargs.get("level", "info"), "message": str(kwargs["message"])})
    return {"provider": "deepseek", "logs": list(_IDE_LOGS), "count": len(_IDE_LOGS)}


__all__ = ["useIdeLogging"]
