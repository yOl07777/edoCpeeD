from __future__ import annotations

from datetime import datetime
from typing import Any


getSessionStartDate = datetime.now


async def getLocalISODate(*_args: Any, **_kwargs: Any) -> str:
    return datetime.now().astimezone().date().isoformat()


async def getLocalMonthYear(*_args: Any, **_kwargs: Any) -> str:
    return datetime.now().astimezone().strftime("%B %Y")


__all__ = ["getSessionStartDate", "getLocalISODate", "getLocalMonthYear"]
