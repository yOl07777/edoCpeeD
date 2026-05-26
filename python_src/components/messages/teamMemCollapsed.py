from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload


async def checkHasTeamMemOps(*args: Any, **kwargs: Any) -> Any:
    ops = kwargs.get("ops") or kwargs.get("operations") or (args[0] if args else []) or []
    return bool(ops)


async def TeamMemCountParts(*args: Any, **kwargs: Any) -> Any:
    ops = kwargs.get("ops") or kwargs.get("operations") or (args[0] if args else []) or []
    return message_payload("team_mem_count_parts", count=len(ops), hasOps=bool(ops))


__all__ = ["TeamMemCountParts", "checkHasTeamMemOps"]
