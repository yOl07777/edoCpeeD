from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload


async def CompactBoundaryMessage(*args: Any, **kwargs: Any) -> Any:
    summary = str(kwargs.get("summary") or (args[0] if args else "Conversation compacted."))
    kept = int(kwargs.get("kept", 0) or 0)
    dropped = int(kwargs.get("dropped", 0) or 0)
    return message_payload("compact_boundary_message", summary=summary, kept=kept, dropped=dropped)


__all__ = ["CompactBoundaryMessage"]
