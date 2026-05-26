from __future__ import annotations

from typing import Any


async def TeamStatus(*args: Any, **kwargs: Any) -> Any:
    members = kwargs.get("members") or (args[0] if args else []) or []
    rows = []
    for index, member in enumerate(members):
        if isinstance(member, dict):
            name = member.get("name") or member.get("agent") or f"member-{index + 1}"
            status = member.get("status") or "idle"
        else:
            name = str(member)
            status = "idle"
        rows.append({"index": index, "name": str(name), "status": str(status)})
    return {"type": "team_status", "provider": "deepseek", "members": rows, "count": len(rows)}


__all__ = ["TeamStatus"]
